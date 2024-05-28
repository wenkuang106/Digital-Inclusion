import streamlit as st

st.image( "http://digitalcharlotte.org/wp-content/uploads/2017/01/DIGITAL-INCLUSION-STOOL-300x300.png", width = 500) #Test of Importing Images
# adding in page Tabs
tab1, tab2, tab3 = st.tabs(["Internet Access", "Device Access", "Digital Literacy"])

with tab1:
    st.header("Internet Access")
    st.image("images/Internet Access Keyboard.jpg")
    st.write('Internet access is the process of connecting to the internet using personal computers, laptops or mobile devices by users or enterprises. Internet access is subject to data signalling rates and users could be connected at different internet speeds. Internet access enables individuals or organizations to avail internet services/web-based services.')

with tab2:
    st.header("Device Access")
    st.image("images/Three Devices.jpg", width=400) 
    st.write("Access Device means any electronic device you use to access mobile or online services or to view electronic documents. This includes, but is not limited to: a traditional computer such as a desktop or laptop computer, or a mobile device such as a tablet computer or a smartphone.")

with tab3:
    st.header("Digital Literacy")
    st.image("images/pic-1-what-is-digital-literacy.png", width=400) 
    st.write("Digital literacy means having the skills you need to live, learn, and work in a society where communication and access to information is increasingly through digital technologies like internet platforms, social media, and mobile devices.")
st.markdown("---")
st.subheader('Understanding Digital Equity, Inclusion & Literacy') #Test of Importing Video
st.video('https://www.youtube.com/watch?v=xfQ8AVmzvbk',start_time=915) #Youtube video
