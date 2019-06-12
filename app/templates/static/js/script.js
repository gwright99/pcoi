console.log('In JS file');

// Event triggers when page is loaded.
window.onload = function() {
	// window.alert('Alert raised!');
	console.log('UL clicked!');
	console.log('past onload event');
	
	
	function toggleOverrideType(button_number){
		console.log('In toggleOverrideType function');
		if (button_number == '0'){
			console.log('Override Type 0 (Express) clicked.');
			express_type_div.setAttribute('class', 'show');
			btg_type_div.setAttribute('class', 'hide');
		} else {
			console.log('Override Type 1 (BTG) clicked.');
			express_type_div.setAttribute('class', 'hide');
			sdm_div.setAttribute('class', 'hide'); // HACK
			btg_type_div.setAttribute('class', 'show');
		}
	};
	
	function toggleSDM(button_number){
		console.log('In toggleSDM function');
		if (button_number == '0'){
			console.log('Express Type 0 (Patient) clicked.');
			sdm_div.setAttribute('class', 'hide');
		} else {
			console.log('Express Type 1 (SDM) clicked.');
			sdm_div.setAttribute('class', 'show');
		}
	};
	
	// Define elements to attach listeners to
	let override_type_0 = document.getElementById('override_type-0');
	let override_type_1 = document.getElementById('override_type-1');
	
	let express_type_div = document.getElementById('express_type');
	let express_type_0 = document.getElementById('express_type-0');
	let express_type_1 = document.getElementById('express_type-1');
	let sdm_div = document.getElementById('sdm');
	
	let btg_type_div = document.getElementById('btg_type');
	
	// Attach listeners
	override_type_0.addEventListener('click', function() {
		toggleOverrideType('0');
	}, false);
	
	override_type_1.addEventListener('click', function() {
		toggleOverrideType('1');
	}, false);
	
	express_type_0.addEventListener('click', function() {
		toggleSDM('0');
	}, false);
	
	express_type_1.addEventListener('click', function() {
		toggleSDM('1');
	}, false);
		
};



	

		
	





	

