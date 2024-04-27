import streamlit as st
from PIL import Image
import re
import pandas as pd
import cv2
import numpy as np
from tensorflow.keras.models import model_from_json

# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()

# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(FirstName TEXT,LastName TEXT,Mobile TEXT,Email TEXT,password TEXT,Cpassword TEXT)')
def add_userdata(FirstName,LastName,Mobile,Email,password,Cpassword):
    c.execute('INSERT INTO userstable(FirstName,LastName,Mobile,Email,password,Cpassword) VALUES (?,?,?,?,?,?)',(FirstName,LastName,Mobile,Email,password,Cpassword))
    conn.commit()
def login_user(Email,password):
    c.execute('SELECT * FROM userstable WHERE Email =? AND password = ?',(Email,password))
    data = c.fetchall()
    return data
def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data
def delete_user(Email):
    c.execute("DELETE FROM userstable WHERE Email="+"'"+Email+"'")
    conn.commit()
    
menu1 = ["Home","Login", "Signup"]
choice1 = st.sidebar.selectbox("menu",menu1)
if choice1=="Home":
    #html
    testp= '# <div style="text-align: center; font-size: 24px; font-weight: bold;">Analysis of MRI images to detect Alzheimer disease using Fine-Tune Transfer Learning</div>'
    st.markdown(testp,unsafe_allow_html=True)
    image=Image.open('Home.png')
    st.image(image)

if choice1=="Login":
    st.subheader("Login Section")
    Email=st.sidebar.text_input('Email')
    password=st.sidebar.text_input('Password',type='password')
    b1=st.sidebar.checkbox("login")
    if b1:
        #Validation
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, Email):
            create_usertable()
            if Email=='a@a.com' and password=='123':
                st.success("Logged In as {}".format("Admin"))
                Email=st.text_input("Delete Email")
                if st.button('Delete'):
                    delete_user(Email)
                user_result = view_all_users()
                clean_db = pd.DataFrame(user_result,columns=["FirstName","LastName","Mobile","Email","password","Cpassword"])
                st.dataframe(clean_db)
            else:
                result = login_user(Email,password)
                if result:
                    imgur=st.file_uploader("Browse MRI Image")
                    if imgur:
                        image=Image.open(imgur)
                        image.save("original.jpg")
                        nimage = cv2.imread("original.jpg")
                        image = cv2.resize(nimage,(128,128))
                        image = image/255.0
                        image = np.array(image).reshape(-1,128,128,3)
                        json_file = open('model.json', 'r')
                        loaded_model_json = json_file.read()
                        json_file.close()
                        model = model_from_json(loaded_model_json)
                        # load weights into new model
                        model.load_weights("model.h5")
                        b2=st.button("Predict")
                        if b2:
                            prediction = model.predict(image)
                            pclass = np.argmax(prediction)
                            categories=['NonDemented', 'VeryMildDemented', 'MildDemented', 'ModerateDemented']
                            org=Image.open('original.jpg')
                            st.image(org)
                            pValue = "Prediction: {0}".format(categories[int(pclass)])
                            st.success(pValue)                      
                else:
                    st.warning("Incorrect Email/Password")  
        else:
            st.warning("Not Valid Email")

if choice1=="Signup":
    st.subheader("Signup Section")
    FirstName=st.text_input('First Name')
    LastName=st.text_input('Last Name')
    Mobile=st.text_input('Contact No')
    Email=st.text_input('Email')
    new_password=st.text_input('Password',type='password')
    Cpassword=st.text_input('Confirm Password',type='password')
    b4=st.button("Sign up")
    if b4:
        if new_password==Cpassword:
            #Validation
            pattern=re.compile("(0|91)?[7-9][0-9]{9}")
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if (pattern.match(Mobile)):
                if re.fullmatch(regex, Email):
                    create_usertable()
                    add_userdata(FirstName,LastName,Mobile,Email,new_password,Cpassword)
                    st.success("You have successfully created a valid Account")
                    st.info("Go to Login Menu to login")
                else:
                    st.warning("Not Valid Email")               
            else:
                st.warning("Not Valid Mobile Number")
        else:
            st.warning("Password Does not Match")
            
            
            
            
            
            