import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyB4TwN8QW2qSXhqD7Oq9EVKzr8ktVftRlE",
  authDomain: "scaler-data-portal.firebaseapp.com",
  projectId: "scaler-data-portal",
  storageBucket: "scaler-data-portal.appspot.com", 
  messagingSenderId: "500359454378",
  appId: "1:500359454378:web:40e63a116eb14be42b3ad3",
  measurementId: "G-7VGWPBK0WR"
};


const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const signInWithGoogle = () => {
  signInWithPopup(auth, provider)
    .then((result) => {
      console.log("✅ User signed in:", result.user.displayName);
    })
    .catch((error) => {
      console.error("❌ Error during sign in:", error);
    });
};

export { signInWithGoogle };
