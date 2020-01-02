fn pow(x, y):
	let a = y
	let b = 1
	while (a >0):
		b = b*x
		a = a-1
	print(b)



print("Sayıların kareleri: ")
let counter = 10
while(counter>0):
	pow::(counter, 2)
	counter = counter -1


print("")

print("Faktoriyeller: ")
fn factorial(x):
	let fact = 1
	while(x>0):
		fact = fact * x
		x = x -1
	print(fact)



let counter = 10 
while(counter>0):
	factorial::(counter)
	counter = counter -1


print("")

print("100'den küçük fibonacci sayıları: ")
fn fib(number):
	let a = 1
	let b = 1
	let temp = 1
	while (b  < number):
		temp = b + a
		a= b
		b = temp 
		print(a)


fib::(100)