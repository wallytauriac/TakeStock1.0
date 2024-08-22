data = {'data1':1, 'data2':2, 'data3':3}
a = {'a1':10, 'a2':20, 'a3':30}
b = {'b1':100, 'b2':200, 'b3':300}

data['a'] = a
data['b'] = b

print(data)
print(data['data1'])
data['a']['a1'] = 15
for key, value in data['a'].items():
    print(key,value)
print(data['a']['a1'])
aa = data['a']
aa['a2'] = 25
data['a'] = aa
print(aa)
print(data)

if __name__ == "__main__":
    print('bye')