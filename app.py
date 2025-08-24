from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

app = Flask(__name__)

# ------------------ Configurations ------------------
app.config['MAIL_SERVER'] = 'smtp.hostinger.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'no-reply@borrowly.in'
app.config['MAIL_PASSWORD'] = 'CqUO7@T0*'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Pavan%402002@localhost:5432/Borrowly'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://borrowly_user:e8QDgeH8ZDsWY1b779OdmML3W293wLTi@dpg-d2esl2mr433s738ff5tg-a.singapore-postgres.render.com/borrowly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

mail = Mail(app)
CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ------------------ Models ------------------
class Borrower(db.Model):
    __tablename__ = 'borrowers'
    id = db.Column(db.String(50), primary_key=True)  # Custom ID format
    # borrower_id = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(200), nullable=False)
    lastname = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    guide_code = db.Column(db.String(200), nullable=True)
    promo_code = db.Column(db.String(200), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Agent(db.Model):
    __tablename__ = 'agents'
    id = db.Column(db.String(50), primary_key=True) 
    # agent_id = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(200), nullable=False)
    lastname = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    guide_code = db.Column(db.String(200), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class LoanEnquiry(db.Model):
    __tablename__ = 'loan_enquiries'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)
    loan_amount = db.Column(db.Integer, nullable=False)
    employment_type = db.Column(db.String(50), nullable=False)
    consent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
# ------------------ Utility Functions ------------------
def generate_otp():
    return str(random.randint(100000, 999999))

def generate_custom_id(firstname, phone):
    """Generate ID as first 4 letters of firstname + last 4 digits of phone"""
    return firstname[:4].upper() + phone[-4:]

def send_otp_email(email, otp):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Your OTP Code</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 30px;">
        <div style="max-width: 500px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); text-align: center;">
            <img src="https://res.cloudinary.com/dxy8blig8/image/upload/v1754302638/WhatsApp_Image_2025-07-30_at_10.51.15_AM_iztnul.jpg" alt="Borrowly Logo" style="height: 60px; margin-bottom: 20px;" />
            <h2 style="color: #00C2CC;">Your <strong>OTP</strong> Code</h2>
            <p style="font-size: 16px; color: #888888;">
                Use the following <strong>One-Time Password (OTP)</strong> to proceed. It is valid for the next 5 minutes.
            </p>
            <div style="font-size: 36px; font-weight: bold; color: #013476; margin: 20px 0;">{{ otp }}</div>
            <p style="font-size: 14px; color: #888888;">If you did not request this, please ignore this email or contact support.</p>
            <br />
            <p style="font-size: 14px; color: #00C2CC;">
                Team Borrowly<br>
                Email: <a href="mailto:support@borrowly.in">support@borrowly.in</a><br>
                Phone: <a href="tel:+917760613515">+91-77606 13515</a>
            </p>
        </div>
    </body>
    </html>
    """
    html = render_template_string(html_template, otp=otp)
    msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.html = html
    mail.send(msg)

# ------------------ Routes ------------------
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    user_type = data.get('user_type')  # 'borrower' or 'agent'
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    dob = data.get('dob')
    gender = data.get('gender')
    state = data.get('state')
    city = data.get('city')
    phone = data.get('phone')
    email = data.get('email')
    raw_password = data.get('password')
    guide_code = data.get('GuideCode') or None
    promo_code = data.get('couponcode') or None if user_type == "borrower" else None

    if user_type not in ['borrower', 'agent']:
        return jsonify({'message': 'Invalid user type. Must be borrower or agent.'}), 400

    if not all([firstname, lastname, dob, gender, state, city, phone, email, raw_password]):
        return jsonify({'message': 'All fields are required.'}), 400
    if user_type == "borrower":
        if Borrower.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered.'}), 400
        if Borrower.query.filter_by(phone=phone).first():
            return jsonify({'message': 'Mobile number already registered.'}), 400
    else:
        if Agent.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered.'}), 400
        if Agent.query.filter_by(phone=phone).first():
            return jsonify({'message': 'Mobile number already registered.'}), 400

    user_id = generate_custom_id(firstname, phone)
    otp = generate_otp()
    hashed_password = generate_password_hash(raw_password)

    if user_type == "borrower":
        new_user = Borrower(
            id=user_id,
            # borrower_id=user_id,
            firstname=firstname,
            lastname=lastname,
            dob=datetime.strptime(dob, "%Y-%m-%d"),
            gender=gender,
            state=state,
            city=city,
            phone=phone,
            email=email,
            password=hashed_password,
            guide_code=guide_code,
            promo_code=promo_code,
            otp=otp,
        )
    else:
        new_user = Agent(
            id=user_id,
            # agent_id=user_id,
            firstname=firstname,
            lastname=lastname,
            dob=datetime.strptime(dob, "%Y-%m-%d"),
            gender=gender,
            state=state,
            city=city,
            phone=phone,
            email=email,
            password=hashed_password,
            guide_code=guide_code,
            otp=otp,
        )

    db.session.add(new_user)
    db.session.commit()
    send_otp_email(email, otp)

    return jsonify({
        'message': f'{user_type.capitalize()} registered successfully. OTP sent to email.',
        'user_id': user_id,
    }), 200


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    user_type = data.get('user_type')

    if not email or not otp or not user_type:
        return jsonify({'message': 'Email, OTP, and user_type are required.'}), 400

    if user_type.lower() == 'borrower':
        user = Borrower.query.filter_by(email=email).first()
    elif user_type.lower() == 'agent':
        user = Agent.query.filter_by(email=email).first()
    else:
        return jsonify({'message': 'Invalid user_type.'}), 400

    if not user:
        return jsonify({'message': f'{user_type.capitalize()} not found.'}), 404

    if user.otp != otp:
        return jsonify({'message': 'Invalid OTP.'}), 400

    user.is_verified = True
    user.status = True
    user.otp = None
    db.session.commit()

    return jsonify({'message': 'Account verified successfully!'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_type = data.get('user_type') 
    email_or_phone = data.get('email_or_phone')
    password = data.get('password')

    if not user_type or not email_or_phone or not password:
        return jsonify({'message': 'user_type, email_or_phone, and password are required.'}), 400

    if user_type.lower() == 'borrower':
        user = Borrower.query.filter(
            (Borrower.email == email_or_phone) | (Borrower.phone == email_or_phone)
        ).first()
    elif user_type.lower() == 'agent':
        user = Agent.query.filter(
            (Agent.email == email_or_phone) | (Agent.phone == email_or_phone)
        ).first()
    else:
        return jsonify({'message': 'Invalid user_type. Must be borrower or agent.'}), 400

    if not user:
        return jsonify({'message': f'{user_type.capitalize()} not found.'}), 404

    if not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid password.'}), 400

    if not user.is_verified:
        return jsonify({'message': 'Account not verified. Please verify your account first.'}), 403

    return jsonify({
        'message': 'Login successful!',
        'user_id': user.id,
        'user_type': user_type.lower()
    }), 200


@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.json
    email = data.get('email') 
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    user_type = data.get('user_type')

    if not all([email, old_password, new_password, confirm_password, user_type]):
        return jsonify({'message': 'All fields are required.'}), 400

    if new_password != confirm_password:
        return jsonify({'message': 'New password and confirm password do not match.'}), 400

    if user_type.lower() == 'borrower':
        user = Borrower.query.filter_by(email=email).first()
    elif user_type.lower() == 'agent':
        user = Agent.query.filter_by(email=email).first()
    else:
        return jsonify({'message': 'Invalid user_type.'}), 400

    if not user:
        return jsonify({'message': f'{user_type.capitalize()} not found.'}), 404

    if not check_password_hash(user.password, old_password):
        return jsonify({'message': 'Old password is incorrect.'}), 400

    if check_password_hash(user.password, new_password):
        return jsonify({'message': 'New password must be different from the old password.'}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully.'}), 200
    
@app.route('/LoanEnquiry', methods=['POST'])
def loan_enquiry():
    data = request.json

    required_fields = [
        'first_name',
        'last_name',
        'mobile_number',
        'email',
        'city',
        'pincode',
        'loan_type',
        'loan_amount',
        'employment_type',
        'consent'
    ]

    for field in required_fields:
        if field not in data or data[field] in [None, '', []]:
            return jsonify({'message': f'Missing or empty field: {field}'}), 400

    if not isinstance(data['consent'], bool) or not data['consent']:
        return jsonify({'message': 'Consent is required to submit loan enquiry.'}), 400

    enquiry = LoanEnquiry(
        first_name=data['first_name'],
        last_name=data['last_name'],
        mobile_number=data['mobile_number'],
        email=data['email'],
        city=data['city'],
        pincode=data['pincode'],
        loan_type=data['loan_type'],
        loan_amount=data['loan_amount'],
        employment_type=data['employment_type'],
        consent=data['consent']
    )

    db.session.add(enquiry)
    db.session.commit()

    return jsonify({'message': 'Loan enquiry submitted successfully!'}), 201

@app.route('/GetLoanEnquiries', methods=['GET'])
def get_all_loan_enquiries():
    enquiries = LoanEnquiry.query.all()

    result = []
    for enquiry in enquiries:
        result.append({
            'id': enquiry.id,
            'first_name': enquiry.first_name,
            'last_name': enquiry.last_name,
            'mobile_number': enquiry.mobile_number,
            'email': enquiry.email,
            'city': enquiry.city,
            'pincode': enquiry.pincode,
            'loan_type': enquiry.loan_type,
            'loan_amount': enquiry.loan_amount,
            'employment_type': enquiry.employment_type,
            # 'consent': enquiry.consent
        })

    return jsonify(result), 200
# ------------------ Run Server ------------------
if __name__ == "__main__":
    app.run(debug=True)


