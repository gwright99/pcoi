from app import app
from flask import render_template, request, flash, redirect
from app.forms import PCOIForm2
from app.forms import sdm_code_system, fhir_override_purpose_code
from app.fhir_resources import related_person_fhir_template
from app.fhir_resources import patient_fhir_template
from app.fhir_resources import practitioner_fhir_template
from app.fhir_resources import organization_fhir_template
from app.fhir_resources import consent_fhir_template
import ast
import json
from flask import jsonify
from flask import Response, make_response
from flask import send_file
import datetime
import PyPDF2
import os
import base64
from io import StringIO, BytesIO, TextIOWrapper
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject

		
@app.route('/pcoi2', methods=['GET', 'POST'])
def pcoi2():
	''' 
		If GET request received, it is our initial transaction.
			Values come from GET params on URL.
		If POST request received, it is the Service self-referring. 
			Values come from form fields plus catch-all to pass the GET values. 
	'''
	
	form = PCOIForm2()
	args = {}
	
	provided_params_get = [
		'system', 
		'org_upi', 'org_name', 
		'provider_upi', 'provider_given_names', 'provider_family_name',
		'patient_hcn', 'patient_given_names', 'patient_family_name',
		'lob_to_override'
	]
	
	provided_params_get_faked = [
		'ConnectingOntario',
		'12345', 'HappyClinic',
		'98765', 'John Paul', 'Jones',
		'55555', 'Homer J', 'Simpson',
		'DHDR,DICS'
	]
	
	provided_params_get_faked_dict = dict(list(zip(provided_params_get, provided_params_get_faked)))
	
	provided_params_form = [
		'override_type',
		'patient_family_name', 'patient_given_names', 'patient_hcn',
		'sdm_family_name', 'sdm_given_names', 'sdm_code',
		'btgi_explanation', 'btgo_explanation',
		'confirm_dhdr_wet_signature',
		'trx_details'
	]
	
	
	# GET REQUEST logic
	if request.method == 'GET':
	
		# Add values for moment transaction received by PCOI Service
		date = datetime.datetime.now()
		args['received_date'] = '{}-{}-{}'.format(date.year, date.month, date.day)
		args['received_time'] = '{}:{}:{}'.format(date.hour, date.minute, date.second)
		
		# Extract all GET parameters in top rectangle (mocking viewer-submitted data)
		# request.args.get returns None if param not present, so used 'if' instead of try/except
		# Example: system = request.args.get("system")
		for param in provided_params_get:
			args[param] = request.args.get(param)
			if args[param] is None:
				print("ERROR! No value for {}. Faking: {}".format(param, 
																provided_params_get_faked_dict[param]))
				args[param] = provided_params_get_faked_dict[param]
		
		return render_template('pcoi2.html', form=form, args=args)
		
		
	# POST REQUEST logic
	if request.method == 'POST':
		
		# GET parameters are separate in first submission to POST, but normalized in args on n+ attempt
		# Try to extract values from request.form['trx_details'], add to args, and then delete key
		try:
			trx_details_string = request.form['trx_details']
			trx_details = ast.literal_eval(trx_details_string)
			args.update(trx_details)
			provided_params_form.remove('trx_details')
		except Exception as e:
			print('[ERROR]: Not trx_details value in provided_params_form array.')
			print(e)
		
		print_args('POST params', request.form) 
		
		for param in provided_params_form:
			try:
				args[param] = request.form[param]
			except KeyError as e:
				# Boolean options only show up if checked. So 'confirm_dhdr_wet_signature' wont be there
				# if not selected, and the 'request.form[x] lookup method fails with KeyException
				if param == 'confirm_dhdr_wet_signature':
					print("WARNING: confirm_dhdr_wet_signature not present. Setting to 'n'.")
					args[param] = 'n'
		
		# Use in-built WTForms validation first, then logic to check that SDM name values present.
		if form.validate() == False:
			print('Validation has failed')
			flash('All fields are required.')
			return render_template('pcoi2.html', form=form, args=args)
			
		if (args['override_type']) == 'ECSDM':
			sdm_fail = False
			if not (args['sdm_family_name'].isalpha()):
				flash('SDM Family Name required')
				sdm_fail = True
			
			if not (args['sdm_given_names'].isalpha()):
				flash('SDM Given Names(s) required')
				sdm_fail = True
				
			if sdm_fail is True:
				print('SDM Given and Family name required.')
				print_args('Failed SDM args', args)
				return render_template('pcoi2.html', form=form, args=args)
				
		# If DHDR is lob to override, make sure confirmation checkbox is checked
		if ('dhdr' in args['lob_to_override'].lower()) and (args['confirm_dhdr_wet_signature'] == 'n'):
			print('DHDR wet signature not confirmed.')
			flash('Must confirm possession of DHDR wet signature before DHDR override can occur.')
			return render_template('pcoi2.html', form=form, args=args)
			

		# If got here, everything is fine. Push values to FHIR resource.
		print_args('Successful Form Args', args)

		fhir_args = generate_fhir_args(args)
		print_args('FHIR Args', fhir_args)
		
		resp = create_FHIR_response(fhir_args)
		return resp
		

def print_args(label, args):
	print('--' * 40)
	print('{} are: {}'.format(label, args))
	print('--' * 40)
	
		
def generate_fhir_args(args):
	# pcoi2 POST endpoint is already passing down most values. Amend as needed.
	
	# Calculate time submission sent to API
	date = datetime.datetime.now()
	args['submitted_date'] = '{}-{}-{}'.format(date.year, date.month, date.day)
	args['submitted_time'] = '{}:{}:{}'.format(date.hour, date.minute, date.second)
	# Add code system value based on sdm_code choice.
	args['sdm_code_system'] = sdm_code_system[args['sdm_code']]
	
	# Split() creates a list where values have single quote. JSON needs dbl-quote.
	# json.dumps() gets the dbl-quote
	# https://cmsdk.com/python/i-want-to-replace-single-quotes-with-double-quotes-in-a-list.html
	args['sdm_given_names'] = json.dumps(args['sdm_given_names'].split())
	args['patient_given_names'] = json.dumps(args['patient_given_names'].split())
	args['provider_given_names'] = json.dumps(args['provider_given_names'].split())
	
	# Override Purpose logic
	override_purpose = args['override_type']
	if (override_purpose == 'ECP') or (override_purpose == 'ECSDM'):
		override_purpose_code = fhir_override_purpose_code['PATRQT']['code']
		override_purpose_display = fhir_override_purpose_code['PATRQT']['display']
	elif (override_purpose == 'BTGI'):
		override_purpose_code = fhir_override_purpose_code['OVRER']['code']
		override_purpose_display = fhir_override_purpose_code['OVRER']['display']
	elif (override_purpose == 'BTGO'):
		override_purpose_code = fhir_override_purpose_code['OVRTPS']['code']
		override_purpose_display = fhir_override_purpose_code['OVRTPS']['display']
	else:
		print('[***ERROR***] OVERRIDE PURPOSE WRONG')
	args['override_purpose'] = override_purpose
	args['override_purpose_code'] = override_purpose_code
	args['override_purpose_display'] = override_purpose_display
	
	return args
	
	
def create_FHIR_response(fhir_args):
	fhir_related_person = related_person_fhir_template.render(args=fhir_args)
	fhir_patient = patient_fhir_template.render(args=fhir_args)
	fhir_practitioner = practitioner_fhir_template.render(args=fhir_args)
	fhir_organization = organization_fhir_template.render(args=fhir_args)
	fhir_consent = consent_fhir_template.render(args=fhir_args)
	
	if (fhir_args['override_type'] == 'ECSDM'):
		response = '[{},{},{},{},{}]'.format(fhir_consent, 
									fhir_patient,
									fhir_related_person,
									fhir_organization,
									fhir_practitioner)
	else:
		response = '[{},{},{},{}]'.format(fhir_consent, 
									fhir_patient,
									fhir_organization,
									fhir_practitioner,)
	
	resp = Response(response=response,  #fhir_related_person,
						status=200,
						mimetype="application/json"
					)
	return resp
	
@app.route('/create_PDF', methods=['GET'])
def create_PDF():
	''' This was really hard to figure out.
	Look at: https://github.com/mstamy2/PyPDF2/issues/355 (Tromar44, Jan 25 2019) 
	entry for details on setup.
	'''
	js_args = request.args.get('args')
	js_args = base64.b64decode(js_args)
	js_args = json.loads(js_args)
	print('js_args are: ', js_args)
	trx_details = js_args['trx_details']
	print('trx_details are: ', trx_details)
	print('trx_details type is: ', type(trx_details))
	trx_details = ast.literal_eval(trx_details)
	print('trx_details type is: ', type(trx_details))

	
	# This is kludged. "pdf_folder" defined in app.__init__
	# Other articles are more elegant in discovering. I've hardcoded.
	input_path = os.path.join(app.pdf_folder, 'scanned_dhdr_w_ids.pdf')
	output_path = os.path.join(app.pdf_folder, 'scanned_dhdr_w_ids_autopopulated.pdf')
	
	# Load field_dictionary with arg values. Then cleanse those fields that contain 
	# the word "undefined"
	
	field_dictionary = {
		'hcp_Health_Number': trx_details['patient_hcn'],
		'hcp_Patient_Name': '{}; {}'.format(trx_details['patient_family_name'], 
											trx_details['patient_given_names']),
		'hcp_Facility': '{} - {}'.format(trx_details['org_upi'],
											trx_details['org_name']),
		'hcp_Consent_Obtained_By': '{}; {}'.format(trx_details['provider_family_name'],
													trx_details['provider_given_names']),
		'hcp_SDM_Type': js_args['sdm_code'],
		'patient_Name_Of_HCP': '{}; {}'.format(trx_details['provider_family_name'],
													trx_details['provider_given_names']),
	}
	
	for k,v in js_args.items():
		if 'undefined' in js_args[k]:
			js_args[k] = ''
	
	# Set hcp_Consent_Provided_By field (Patient vs SDM)
	if (js_args['override_type'] == 'ECSDM'):
		print('SDM values found')
		field_dictionary['hcp_Consent_Provided_By_SDM'] = 'X'
		field_dictionary['patient_Name_Of_SDM'] = '{}; {}'.format(js_args['sdm_family_name'], 
											js_args['sdm_given_names'])	
	else:
		field_dictionary['hcp_Consent_Provided_By_Patient'] = 'X'
		field_dictionary['patient_Name_Of_SDM'] = field_dictionary['hcp_Patient_Name']
		
	# Set the date and time form was generated
	date = datetime.datetime.now()
	field_dictionary['hcp_Date'] = '{}-{}-{}'.format(date.year, date.month, date.day)
	field_dictionary['hcp_time'] = '{}:{}:{}'.format(date.hour, date.minute, date.second)
	field_dictionary['patient_Date'] = '{}-{}-{}'.format(date.year, date.month, date.day)

	#------------ Create PDF logic -----------
	infile = input_path
	outfile = output_path
	
	def set_need_appearances_writer(writer: PdfFileWriter):
		# See 12.7.2 and 7.7.2 for more information: http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
		try:
			catalog = writer._root_object
			# get the AcroForm tree
			if "/AcroForm" not in catalog:
				writer._root_object.update({
					NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

			need_appearances = NameObject("/NeedAppearances")
			writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
			return writer
		except Exception as e:
			print('set_need_appearances_writer() catch : ', repr(e))
			return writer

	# Uncomment if PDF generation breaks & re-indent ifs below
	#with open(infile, 'rb') as f:
	#	pdf = PdfFileReader(f)
	
	pdf = PdfFileReader(open(infile, "rb"), strict=False)	
	if "/AcroForm" in pdf.trailer["/Root"]:
		pdf.trailer["/Root"]["/AcroForm"].update(
			{NameObject("/NeedAppearances"): BooleanObject(True)})

	pdf2 = PdfFileWriter()
	set_need_appearances_writer(pdf2)
	if "/AcroForm" in pdf2._root_object:
		pdf2._root_object["/AcroForm"].update(
			{NameObject("/NeedAppearances"): BooleanObject(True)})

	pdf2.addPage(pdf.getPage(0))
	pdf2.updatePageFormFieldValues(pdf2.getPage(0), field_dictionary)

	# See https://www.blog.pythonlibrary.org/2013/07/16/pypdf-how-to-write-a-pdf-to-memory/
	# for writing PDF to memory
	
	# This successfully writes a PDF to file
	outputStream = open(outfile, "wb")
	pdf2.write(outputStream)
		
	
	# THIS RETURNS pdf with values!!!!
	# ALWAYS DELETE BROWSER CACHE - this was only returning text before
	# https://www.reddit.com/r/learnpython/comments/4b456s/using_flask_to_return_pdfs_how_do_i_do_it/
	# https://stackoverflow.com/questions/41731457/flask-force-download-pdf-files-to-open-in-browser
	# https://gist.github.com/widoyo/3897853
	# https://stackoverflow.com/questions/18281433/flask-handling-a-pdf-as-its-own-page
	tmp = BytesIO()
	pdf2.write(tmp)
	resp = make_response(tmp.getvalue(), 200)
	resp.headers['Content-Disposition'] = "inline; filename=%s" % 'populated_pdf.pdf'
	resp.mimetype = "application/pdf"
	return resp
	
	'''
	# This returns text in PDF only too
	# https://gist.github.com/Miserlou/fcf0e9410364d98a853cb7ff42efd35a
	with open(outfile, "rb") as pdf_to_send:
		return send_file(
			BytesIO(pdf_to_send.read()),
			attachment_filename='popped_pdf.pdf',
			mimetype="application/pdf"
		)'''
	
	'''
	#resp = Response(tmp.getvalue())
	resp.headers['Content-Disposition'] = "inline; filename=%s" % 'populated_pdf.pdf'
	resp.mimetype = "application/pdf"
	return resp
	
	return send_file(tmp.getvalue(),
				mimetype="application/pdf",
				as_attachment=True,
				attachment_filename="populated_PDF.pdf"
	)
	resp = Response(response=tmp,
						status=400,
						mimetype="application/pdf"
					)
	return resp'''
	
	
