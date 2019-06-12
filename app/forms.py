from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField 
from wtforms import SelectField, SubmitField, RadioField, TextField, TextAreaField
from wtforms import validators, ValidationError

# http://www.hl7.org/FHIR/2016May/valueset-patient-contact-relationship.html
sdm_code_options = [('ATTPC', 'Attorney for Personal Care'), 
					('CCBOARDREP', 'Representative Appointed by Consent and Capacity Board'), 
					('CHILD', 'Child'),
					('EXT', 'Extended Family Member'),
					('GUARD', 'Guardian'),
					('PRN', 'Parent'),
					('SIB', 'Sibling'),
					('SPS', 'Spouse')]	

sdm_code_system = {
	'ATTPC': 'http://ehealthontario.ca/fhir/NamingSystem/ca-on-personal-relationship',
	'CCBOARDREP': 'http://ehealthontario.ca/fhir/NamingSystem/ca-on-personal-relationship',
	'CHILD': 'http://hl7.org/fhir/v3/RoleCode',
	'EXT': 'http://hl7.org/fhir/v3/RoleCode',
	'GUARD': 'http://hl7.org/fhir/v3/RoleCode',
	'PRN': 'http://hl7.org/fhir/v3/RoleCode',
	'SIB': 'http://hl7.org/fhir/v3/RoleCode',
	'SPS': 'http://hl7.org/fhir/v3/RoleCode'
}

fhir_override_purpose_code = {
	'OVRER': {
		'code': 'OVRER',
		'display': 'emergency treatment override'
	},
	'OVRTPS': {
		'code': 'OVRTPS',
		'display': 'third party safety override'
	},
	'PATRQT': {
		'code': 'PATRQT',
		'display': 'in response to patient request'
	}
}
							

class PCOIForm2(FlaskForm):
	override_type = RadioField('Override Type', 
								choices = [('ECP', '1. Express consent obtained from patient'), 
											('ECSDM', '2. Express consent obtained from Substitute Decision Maker (SDM)'),
											('BTGI', '3. Significant risk of bodily harm to individual'),
											('BTGO', '4. Significant risk of bodily harm to others')],
								render_kw={'id': 'override_type'}
							)

	patient_given_names = TextField("Patient Given Name(s)",
								render_kw={'readonly': True,
									'id': 'patient_given_names'})
	patient_family_name = TextField("Patient Family Name", 
								render_kw={'readonly': True,
									'id': 'patient_family_name'})
	patient_hcn = TextField("Patient HCN", 
									render_kw={'readonly': True,
										'id': 'patient_hcn'})
	
	sdm_given_names = TextField("SDM Given Name(s)", 
									render_kw={'id': 'sdm_given_names'})
	sdm_family_name = TextField("SDM Family Name", 
									render_kw={'id': 'sdm_family_name'})
	sdm_code = SelectField("Relationship to Patient",
									choices= sdm_code_options,
									render_kw={'id': 'sdm_code'}) #'id': 'sdm_relationship'
									
	trx_details = TextField("Hidden Field to Pass Patient/Provider Details",
								render_kw={'id': 'trx_details'}
							)
							
	btgi_explanation = TextAreaField('Reason for override',
										render_kw={"rows": 4, "cols": 80})
										
	btgo_explanation = TextAreaField('Reason for override',
										render_kw={"rows": 4, "cols": 80})									
	
	confirm_dhdr_wet_signature = BooleanField('I confirm a signed DHDR override form',
										render_kw={'id': 'confirm_dhdr_wet_signature'})
										
	submit = SubmitField('Submit Override')
	

