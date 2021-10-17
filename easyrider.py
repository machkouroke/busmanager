import json
import re

data = json.loads(input())


def stop_name(x):
    match = re.match(r'[A-Z].+ (Road|Boulevard|Avenue|Street)$', x)
    return bool(isinstance(x, str) and match)


def stop_type(y):
    match = re.match(r'[SOF]?$', y)
    return bool(isinstance(y, str) and match)


def a_time(z):
    match = re.match(r'([0-1][0-9]|2[0-4]):[0-5][0-9]$', z)
    return bool(isinstance(z, str) and match)


validator = {
    "bus_id": lambda x: isinstance(x, int) and x != '',
    "stop_id": lambda x: isinstance(x, int) and x != '',
    "stop_name": lambda x: stop_name(x),
    'next_stop': lambda x: isinstance(x, int) and x != '',
    'stop_type': lambda x: stop_type(x),
    'a_time': lambda x: a_time(x),
}


def data_type_validator():
    error_dict = {x: 0 for x in data[0]}
    for x in data:
        for y in x:
            if not validator[y](x[y]):
                error_dict[y] += 1
    print(f'Format validation: {sum(error_dict.values())} errors')
    for i, value in error_dict.items():
        if i in {'stop_name', 'stop_type', 'a_time'}:
            print(f'{i}: {value}')


def stops_counter():
    stops_dict = {x: 0 for x in {x['bus_id'] for x in data}}
    for x in data:
        stops_dict[x['bus_id']] += 1
    print('Line names and number of stops:')
    for i, value in stops_dict.items():
        print(f'bus_id: {i}, stops: {value}')


def arrival():
    line_counter = {x: {'S': [], 'F': []} for x in {x['bus_id'] for x in data}}
    for x in data:
        if x['stop_type'] == 'S':
            line_counter[x['bus_id']]['S'].append(x['stop_name'])
        elif x['stop_type'] == 'F':
            line_counter[x['bus_id']]['F'].append(x['stop_name'])
    return line_counter


def special_top(mode='m'):
    line_counter = arrival()
    for x, value in line_counter.items():
        if len(value['S']) != 1 or len(value['F']) != 1:
            if mode == 'm':
                print(f'There is no start or end stop for the line: {x}.')
            return
    top_dict = {x: [] for x in ('Start stops', 'Transfer stops', 'Finish stops')}
    top_dict['Start stops'] = {line_counter[x]['S'][0] for x in line_counter}
    top_dict['Finish stops'] = {line_counter[x]['F'][0] for x in line_counter}
    line_counter = {x: {y['stop_name'] for y in data if y['bus_id'] == x} for x in {x['bus_id'] for x in data}}
    li = [line_counter[x] for x in line_counter]
    transfer = []
    for x in li:
        for y in li:
            if y != x:
                transfer.append(x & y)
    if not transfer:
        return 0
    top_dict['Transfer stops'] = set.union(*transfer)
    for i, x in top_dict.items():
        if mode == 'm':
            print(f'{i}: {len(x)} {sorted(x)}')
    return top_dict


def bool_eval(value: list):
    t = True
    for i in value:
        t = t and i
    return t


def d_o(a: str, b: str) -> bool:
    c, d = [x.split(':') for x in (a, b)]
    c, d = [int(x) for x in c], [int(x) for x in d]
    return c[0] <= d[0] and (c[0] < d[0] or c[1] < d[1])


def unloose_time():
    line = {x: [] for x in {x['bus_id'] for x in data}}
    i = 0
    for x in line:
        for y in data[i:]:
            if y['bus_id'] == x:
                line[x].append((y["stop_name"], y['a_time']))
                i += 1
                continue
            break
    error = {x: [(d_o(line[x][j][1], line[x][j + 1][1]), line[x][j + 1][0])
                 for j in range(len(line[x]) - 1)] for x in line}
    valid = {x: [y[0] for y in error[x]] for x in error}
    stop = {x: [y[1] for y in error[x]] for x in error}
    answer = {x: bool_eval(valid[x]) for x in valid}
    print('Arrival time test:')
    if False not in answer.values():
        print('OK')
        return
    for i, x in valid.items():
        for j in range(len(x)):
            if not x[j]:
                print(f'bus_id line {i}: wrong time on station {stop[i][j]}')
                break


def on_demand():
    station = special_top(mode='w')
    if station:
        banned_value = set.union(*station.values())
        error = {
            x['stop_name']
            for x in data
            if x['stop_type'] == 'O' and x['stop_name'] in banned_value
        }
    else:
        error = 0
    print('On demand stops test:')
    if error:
        print(f'Wrong stop type: {sorted(list(error))}')
    else:
        print('OK')


if __name__ == '__main__':
    on_demand()
