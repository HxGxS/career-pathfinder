#!/usr/bin/env python3
# Adapted for Career Pathfinder from the job-application-assistant workflow.
# Licensed under the MIT License; see README.md (Credits and licence).
"""Decide whether the browser-header retry in .claude/skills/career-job-search/SKILL.md may run.

The retry exists to get past bot-filtering firewalls on sites whose robots.txt
permits access. It is never used to override a site that has said no.

WebFetch identifies itself as Claude-User and honors robots.txt, so a 403 has
two very different causes: a firewall default on a site whose published policy
allows access, or a site that has actually declined. This tells them apart.

Rules implemented (RFC 9309), deliberately on the cautious side:
  * longest-match wins; on equal specificity Disallow wins
  * a Disallow for either "*" or "Claude-User" blocks the retry
  * blank lines inside a record do not end it (Python's robotparser drops
    rules in that case, which fails open)
  * one leading UTF-8 byte-order mark is skipped (left in, it hides a first
    "User-agent" line and drops that whole group, which fails open)
  * 404 means no published policy, which is permission
  * any other failure to read robots.txt leaves permission unconfirmed,
    and the retry does not happen - including a User-agent, Allow or
    Disallow line holding U+FFFD, i.e. a byte that is not valid UTF-8
  * only an http or https URL with a host is checked at all; anything else
    is unconfirmed without a request, and curl itself is pinned to http(s)
    on the first hop and on every redirect

Usage:  python3 scripts/robots_check.py <url>
Exit 0 = the retry may proceed. Exit 1 = do not retry; go to escalation step 4
(search for the employer's own posting).
"""

import re, subprocess, sys
from urllib.parse import urlsplit, unquote

BROWSER = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
           '(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

NEXT_STEP = 'do not retry, go to step 4 (search for the employer\'s own posting)'


def _fetch(url, ua):
    """curl, not urllib: some hosts hang urllib indefinitely while answering
    curl in under a second, and --max-time is a hard ceiling."""
    # "--" ends option parsing, so a URL beginning with a dash is never read as
    # a flag. --proto pins the first hop to http(s) and --proto-redir every
    # redirect -L follows, so neither the caller nor the site can steer curl to
    # file:, gopher:, ftp: or any other protocol it was built with.
    r = subprocess.run(
        ['curl', '-sS', '-L', '--proto', '=http,https', '--proto-redir', '=http,https',
         '--max-redirs', '5', '--max-time', '12', '-A', ua,
         '-H', 'Accept: text/plain,*/*', '-w', '\n%{http_code}', '--', url],
        # robots.txt is UTF-8 (RFC 9309); pin the decoding so a host default
        # code page can't break the pipe reader.
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=20)
    if r.returncode != 0:
        raise RuntimeError('curl exit %d' % r.returncode)
    body, _, code = r.stdout.rpartition('\n')
    return body, int(code or 0)


def is_robots_body(text):
    """Does this actually look like a robots.txt?

    A misconfigured host can answer /robots.txt with 200 and an HTML error page.
    That body parses to zero rules, and zero rules read as "allowed" - so a
    soft-200 would grant permission that was never given. An empty or
    whitespace-only body IS a valid allow-all under RFC 9309 and stays allowed;
    a non-empty body with no recognised directive is treated as unreadable.
    """
    text = text.removeprefix('﻿')          # byte-order mark, see _groups
    if not text.strip():
        return True
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip().lower()
        if ':' in line and line.split(':', 1)[0].strip() in (
            'user-agent', 'allow', 'disallow', 'sitemap', 'crawl-delay', 'host',
        ):
            return True
    return False


def has_undecodable_rule(text):
    """Does a User-agent, Allow or Disallow line hold U+FFFD?

    U+FFFD stands in for a byte that did not decode as UTF-8. A robots.txt saved
    in a legacy code page with raw non-ASCII bytes in a rule yields a pattern
    that can never match: the rule would be silently skipped and the path read
    as allowed. Such a body is unreadable, not permissive. The field is named
    with U+FFFD removed, so a stray byte before "Disallow" cannot hide the line.
    U+FFFD in a comment or in any other field decides nothing and is ignored.
    """
    for raw in text.removeprefix('﻿').splitlines():
        line = raw.split('#', 1)[0]
        if '�' in line and ':' in line:
            field = line.split(':', 1)[0].replace('�', '').strip().lower()
            if field in ('user-agent', 'allow', 'disallow'):
                return True
    return False


def _groups(text):
    """user-agent -> [(is_allow, pattern)], tolerating blank lines inside a record.

    One leading U+FEFF is skipped, as Google's reference parser does. Otherwise
    a file saved with a UTF-8 byte-order mark hides its first field: a leading
    "User-agent: *" goes unseen, every rule in its group is dropped, and
    "Disallow: /" reads as allow-all.
    """
    out, agents, expect = {}, [], True
    for raw in text.removeprefix('﻿').splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or ':' not in line:
            continue
        field, _, value = line.partition(':')
        field, value = field.strip().lower(), value.strip()
        if field == 'user-agent':
            if not expect:
                agents, expect = [], True
            agents.append(value.lower())
            out.setdefault(value.lower(), [])
        elif field in ('allow', 'disallow') and agents:
            expect = False
            for a in agents:
                out[a].append((field == 'allow', value))
    return out


def _match(pattern, path):
    """RFC 9309 wildcard match; returns match length or -1.

    The pattern is percent-decoded to match the already-decoded path, so
    "Disallow: /foo%20bar" matches "/foo bar". Under RFC 9309 section 2.2.2,
    '$' anchors the end of the URL only at the end of the pattern; a '$'
    elsewhere is matched literally.

    Matching is a table walk in O(len(pattern) * len(path)), never a regex: a
    regex built from a site-controlled pattern with repeated wildcards can take
    exponential time. Consecutive '*' match as one, as RFC 9309 implies.
    """
    if pattern == '':
        return -1
    pattern = unquote(pattern)
    end_anchor = pattern.endswith('$')
    pat = re.sub(r'\*{2,}', '*', pattern[:-1] if end_anchor else pattern)
    # reach[j] is True when the first j pattern characters match the path
    # consumed so far. A '*' extends a match over any character (reach[j]
    # carries forward) and also matches nothing (reach[j-1] on the same row).
    reach = [True] + [False] * len(pat)
    for j, c in enumerate(pat, 1):
        if c != '*':
            break
        reach[j] = True
    if reach[-1] and not end_anchor:
        return len(pattern)
    for ch in path:
        step = [False] * (len(pat) + 1)
        for j, c in enumerate(pat, 1):
            if c == '*':
                step[j] = step[j - 1] or reach[j]
            elif c == ch:
                step[j] = reach[j - 1]
        reach = step
        if reach[-1] and not end_anchor:
            return len(pattern)      # a prefix match is enough without '$'
    return len(pattern) if reach[-1] else -1


def allowed(text, agent, path):
    g = _groups(text)
    rules = g.get(agent.lower()) or g.get('*') or []
    best_len, best_allow = -1, True
    for is_allow, pat in rules:
        n = _match(pat, path)
        if n > best_len or (n == best_len and n >= 0 and not is_allow):
            best_len, best_allow = n, is_allow      # ties -> Disallow wins (cautious)
    return True if best_len < 0 else best_allow


def gate(url):
    parts = urlsplit(url)  # urlsplit lower-cases the scheme
    # Only http(s) with a host is a page this tool can have a policy for; any
    # other input fails closed before curl is asked anything.
    if parts.scheme not in ('http', 'https'):
        return 1, f'UNCONFIRMED (unsupported URL scheme {parts.scheme!r}) - {NEXT_STEP}'
    if not parts.netloc:
        return 1, f'UNCONFIRMED (no host in the URL) - {NEXT_STEP}'
    path = unquote(parts.path) or '/'
    if parts.query:
        path += '?' + unquote(parts.query)
    robots = f'{parts.scheme}://{parts.netloc}/robots.txt'
    body, last = None, 'no attempt'
    # Ask honestly first; if a firewall refuses even robots.txt, read it as a
    # browser and then obey it strictly - a policy you can't read can't be honoured.
    for ua in ('Claude-User', BROWSER):
        try:
            text, code = _fetch(robots, ua)
        except Exception as e:
            last = type(e).__name__
            continue
        if code == 404:
            return 0, 'ALLOWED - no robots.txt published'
        if code == 200:
            if not is_robots_body(text):
                last = 'HTTP 200 but the body is not a robots.txt'
                continue
            if has_undecodable_rule(text):
                last = 'HTTP 200 but a User-agent/Allow/Disallow line is not valid UTF-8'
                continue
            body = text
            break
        last = 'HTTP %d' % code
    if body is None:
        return 1, f'UNCONFIRMED ({last}) - {NEXT_STEP}'
    for a in ('Claude-User', '*'):
        if not allowed(body, a, path):
            return 1, f'DISALLOWED for {a} - {NEXT_STEP}'
    return 0, 'ALLOWED - robots.txt permits this path'


def _force_utf8_output() -> None:
    """Write UTF-8 whatever the host's default encoding is."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)  # absent on a StringIO under test
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == '__main__':
    _force_utf8_output()
    if len(sys.argv) != 2:
        print('usage: python3 scripts/robots_check.py <url>', file=sys.stderr)
        sys.exit(2)
    rc, msg = gate(sys.argv[1])
    print(msg)
    sys.exit(rc)
