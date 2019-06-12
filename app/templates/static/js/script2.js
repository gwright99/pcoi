console.log('In JS file');

// Event triggers when page is loaded.
window.onload = function() {
	// window.alert('Alert raised!');
	console.log('past onload event');
	
	
	function toggleOverrideType(button_number){
		console.log('In toggleOverrideType function');
		if (button_number == '0'){
			console.log('Override Type 0 clicked.');
			patient_div.setAttribute('class', 'show');
			sdm_div.setAttribute('class', 'hide');
			btgi_div.setAttribute('class', 'hide');
			btgo_div.setAttribute('class', 'hide');
		} else if (button_number == '1') {
			console.log('Override Type 1 clicked.');
			patient_div.setAttribute('class', 'hide');
			sdm_div.setAttribute('class', 'show');
			btgi_div.setAttribute('class', 'hide');
			btgo_div.setAttribute('class', 'hide');
		} else if (button_number == '2') {
			console.log('Override Type 2 clicked.');
			patient_div.setAttribute('class', 'hide');
			sdm_div.setAttribute('class', 'hide');
			btgi_div.setAttribute('class', 'show');
			btgo_div.setAttribute('class', 'hide');
		} else if (button_number == '3') {
			console.log('Override Type 3 clicked.');
			patient_div.setAttribute('class', 'hide');
			sdm_div.setAttribute('class', 'hide');
			btgi_div.setAttribute('class', 'hide');
			btgo_div.setAttribute('class', 'show');	
		} else {
			console.log('OOPS - Something went wrong.');
		}
	};
	
	// Define elements to attach listeners to
	// NOTE difference between _ and - on the zero
	let override_ul = document.getElementById('override_type');
	let override_type_0 = document.getElementById('override_type-0');
	let override_type_1 = document.getElementById('override_type-1');
	let override_type_2 = document.getElementById('override_type-2');
	let override_type_3 = document.getElementById('override_type-3');

	//let patient_div = document.getElementById('patient_div');
	let patient_div = document.getElementById('patient_div');
	let sdm_div = document.getElementById('sdm_div');
	let btgi_div = document.getElementById('btgi_div');
	let btgo_div = document.getElementById('btgo_div');
	
	// Append div experiment
	//override_ul.children[0].appendChild(patient_div);
	override_ul.children[0].appendChild(patient_div);
	override_ul.children[1].appendChild(sdm_div);
	override_ul.children[2].appendChild(btgi_div);
	override_ul.children[3].appendChild(btgo_div);
	
	// Attach listeners
	override_type_0.addEventListener('click', function() {
		toggleOverrideType('0');
	}, false);
	
	override_type_1.addEventListener('click', function() {
		toggleOverrideType('1');
	}, false);
	
	override_type_2.addEventListener('click', function() {
		toggleOverrideType('2');
	}, false);
	
	override_type_3.addEventListener('click', function() {
		toggleOverrideType('3');
	}, false);	
};

function getpdf() {
	
		// Logic:
		// 1) Get values from the HTML page
		// 2) Add to JSON object
		// 3) Stringify JSON object
		// 4) Convert to B64 (to handle spaces in the values
		// 5) Send to create_PDF API on Flask
	
		// Get variable values needed for (1) HCP section of override form
		let trx_details = document.getElementById('trx_details').value
		//let patient_given_names = document.getElementById('patient_given_names').value;
		//let patient_family_name = document.getElementById('patient_family_name').value;
		let sdm_given_names = document.getElementById('sdm_given_names').value;
		let sdm_family_name = document.getElementById('sdm_family_name').value;
		//let provider_given_names = document.getElementById('provider_given_names').value;
		//let provider_family_name = document.getElementById('provider_family_name').value;
		//let org_upi = document.getElementById('org_upi').value;
		//let org_name = document.getElementById('org_name').innerText;
		
		//let hcp_Health_Number = document.getElementById('patient_hcn').value;
		//let hcp_Patient_Name = patient_family_name + ', ' + patient_given_names;
		//let hcp_Facility = org_upi + ' - ' + org_name;
		//let hcp_Consent_Obtained_By = provider_family_name + ', ' + provider_given_names;
		let e = document.getElementById('sdm_code')
		let sdm_code = e.options[e.selectedIndex].value;
		// this gets value of the override selected
		let override_type = document.querySelector('input[name="override_type"]:checked').value;
		
		// Get variable values needed for (2) Patient/SDM section of override form
		//let patient_Name_Of_HCP = provider_family_name + ', ' + provider_given_names;
		let patient_Name_Of_SDM = sdm_family_name + ', ' + sdm_given_names;
		
		// Most details alreayd in trx_details hidden field. Grab SDM value from form too.
		args = {
			"sdm_given_names" : sdm_given_names,
			"sdm_family_name" : sdm_family_name,
			"override_type": override_type,
			"sdm_code": sdm_code,
			"trx_details": trx_details
		};
		
		// Convert None-type to blank string so as not to break Python code.
		// See: https://stackoverflow.com/questions/31096596/why-is-foreach-not-a-function-for-this-object/31096661
		Object.keys(args).forEach(function(key) {
			console.log(args[key]);
			/*if (args[key].includes('undefined')) {
				args[key] = '';
			}*/
		});
		
		args = JSON.stringify(args);
		console.log('Args are: ', args);
		args = btoa(args);
		console.log('BTOA Args are: ', args);
		
		/*
		let pdf_params = '?' +
			'hcp_Health_Number=' + hcp_Health_Number + '&' + 
			'hcp_Patient_Name=' + hcp_Patient_Name + '&' + 
			'hcp_Facility=' + hcp_Facility + '&' + 
			`hcp_Consent_Obtained_By=${hcp_Consent_Obtained_By}` + '&' + 
			`hcp_SDM_Type=${hcp_SDM_Type}` + '&' + 
			`patient_Name_Of_HCP=${patient_Name_Of_HCP}` + '&' + 
			`patient_Name_Of_SDM=${patient_Name_Of_SDM}`;
			
		pdf_params = pdf_params.replace(' ', '%20');
		
		*/
		
		let api_base = 'http://localhost:5000/create_PDF?';
		// let api_full = api_base + pdf_params;
		let api_full = api_base + 'args=' + args;
		console.log('Api full is', api_full);
		
		window.open(api_full, '_blank'); // "https://www.google.com"
		/* 
		// https://blog.jayway.com/2017/07/13/open-pdf-downloaded-api-javascript/
		function showFile(blob){
			// It is necessary to create a new blob object with mime-type explicitly set
			// otherwise only Chrome works like it should
			var newBlob = new Blob([blob], {type: "application/pdf"})
 
			// IE doesn't allow using a blob object directly as link href
			// instead it is necessary to use msSaveOrOpenBlob
			if (window.navigator && window.navigator.msSaveOrOpenBlob) {
				window.navigator.msSaveOrOpenBlob(newBlob);
				return;
			} 
 
			// For other browsers: 
			// Create a link pointing to the ObjectURL containing the blob.
			const data = window.URL.createObjectURL(newBlob);
			var link = document.createElement('a');
			link.href = data;
			//link.download="file.pdf";
			link.click();
			setTimeout(function(){
				// For Firefox it is necessary to delay revoking the ObjectURL
				document.body.removeChild(link);
				window.URL.revokeObjectURL(data); 
			}, 100);
		};
		
		fetch(api_full)
		.then(r => r.blob())
		.then(showFile) */
		
	};
