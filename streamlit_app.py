import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Initialize the active Snowflake session

cnx = st.connection("snowflake")
session =cnx.session()

# Streamlit App Title
st.title("Welcome to the Gen Z Navigator")

# Create a sidebar with options
st.sidebar.header("Navigation")
st.sidebar.markdown(
    """
    **Welcome to the Gen Z Navigator!**  
    Please select one of the options below to proceed:  
    - **Youth Registration**: If you are a youth seeking job opportunities, register your details here.
    - **Employer Registration**: If you are an employer looking to hire youth, register your organization and view youth profiles.
    """
)

option = st.sidebar.selectbox("Select an Option", ["Youth Registration", "Employer Registration"])

# Youth Registration Section
if option == "Youth Registration":
    st.header("Youth Registration for Sustainable Job Opportunities")

    # Collect user data
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=18, max_value=60)
    state = st.text_input("State")
    district = st.text_input("District")  # New field for District
    education = st.selectbox("Education Level", ["No Formal Education", "High School", "Diploma", "Bachelor's", "Master's", "PhD"])
    email = st.text_input("Email Address")
    contact = st.text_input("Contact Information (Phone)")
    aadhaar = st.text_input("Aadhar Number")  # New field for Aadhar Number
    interests = st.text_area("Your Interests (e.g., Property Maintenance, Caregiving)")
    skills = st.text_area("Your Skills")
    availability = st.selectbox("Availability", ["Full-time", "Part-time"])

    # Button to submit registration
    if st.button('Submit Registration'):
        # Validate required fields
        if not name or not state or not district or not email or not contact or not aadhaar or not interests or not skills:
            st.error("Please fill in all required fields!")
        else:
            try:
                # Check if the applicant already exists by Aadhaar, Email, or Contact
                check_duplicate_stmt = f"""
                    SELECT * FROM SFHACKTON.PUBLIC.APPLICANTS 
                    WHERE ADHAAR_NUMBER = '{aadhaar}' OR EMAIL = '{email}' OR CONTACT = '{contact}'
                """
                duplicate_check = session.sql(check_duplicate_stmt).collect()

                if duplicate_check:
                    st.error(f"An applicant with the same Aadhaar Number, Email, or Contact Information already exists.")
                else:
                    # If no duplicates, insert the new applicant's data
                    insert_stmt = """
                        INSERT INTO SFHACKTON.PUBLIC.APPLICANTS 
                        (NAME, AGE, STATE, DISTRICT, EDUCATION, EMAIL, CONTACT, ADHAAR_NUMBER, INTERESTS, SKILLS, AVAILABILITY)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    session.sql(insert_stmt, (name, age, state, district, education, email, contact, aadhaar, interests, skills, availability)).collect()

                    st.success(f'Your information has been submitted successfully, {name}!', icon="✅")

            except Exception as error:
                st.error(f"An error occurred: {error}")

# Employer Registration Section
elif option == "Employer Registration":
    st.header("Empower Unemployed Youth for Sustainable Jobs")

    # Employer Registration
    st.subheader("Register as an Employer")
    employer_name = st.text_input("Employer Name")
    employer_contact = st.text_input("Contact Information (Email/Phone)")
    adhar_or_passport = st.text_input("Aadhar/Passport Number")

    # View Youth Details
    st.subheader("View Youth Profiles")
    youth_df = session.table("applicants").select("APPLICANT_ID", "name", "skills", "state", "district", "education", "interests", "availability").to_pandas()
    st.dataframe(youth_df)

    # Selection box for youth profiles
    selected_youth_id = st.selectbox("Select Youth Profile", youth_df["APPLICANT_ID"])

    if st.button('Register Employer'):
        if not employer_name or not employer_contact or not adhar_or_passport:
            st.error("Please fill in all required fields!")
        else:
            # Insert employer information into the employers table
            session.sql(
                f"""
                INSERT INTO EMPLOYERS (NAME, CONTACT_INFO, ADHAR_PASSPORT_NUMBER, SELECTED_YOUTH_ID) 
                VALUES ('{employer_name}', '{employer_contact}', '{adhar_or_passport}', '{selected_youth_id}')
                """
            ).collect()
            st.success(f'Employer {employer_name} registered successfully!')

    st.success('YOU WILL GET THE SELECTED APPLICANT DETAILS SHORTLY. TO YOUR MOBILE NUMBER THANK YOU!!!', icon="👍")
