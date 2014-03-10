import yappi

def impl():
    out = '''
    <p> Profile is{0}running. 
    <a href='start'>Start</a> <a href='stop'>Stop</a> <a href='clear_stats'>Clear stats</a>
    '''.format(
        ' ' if yappi.is_running() else ' not '
    )
    fkeys = 'index module lineno name ncall nactualcall builtin ttot tsub tavg'.split()
    out += '<table><tr>{0}</tr>'.format(''.join(map('<th>{0}</th>'.format, fkeys)))
    fmt = '<tr>{0}</tr>'.format(''.join('<td>{0.%s}</td>' % (k, ) for k in fkeys))
    out += ''.join(map(fmt.format, yappi.get_func_stats()))
    out += '</table>'
    return out
