// Setting and Swapping
var myNumber = 42;
var myName = Robert;

myNumber = myName;
myName = myNumber;

//Print -52 to 1066
for (var = -52; i < 1067; i++) {
	console.log(i);
}

//Don't Worry, Be Happy
function beCheerful() {
	for (var i = 1; i < 99; i++) {
		console.log('good morning!')
	}
}
beCheerful();

// Mulitples of Three - but Not All
for (var i = -300; i > 0; i++) {
	if (i === -6) {
		break;
	}
	if (i === -3) {
		break;
	}
	console.log(i);
}