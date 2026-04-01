import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDk2RSYQH3LO7uq3jBLNAGGFoqmSUefWJI",
  authDomain: "cinealert-6dbc7.firebaseapp.com",
  projectId: "cinealert-6dbc7",
  storageBucket: "cinealert-6dbc7.firebasestorage.app",
  messagingSenderId: "942773833105",
  appId: "1:942773833105:web:4886a56f003b94a7fb5e30",
  measurementId: "G-24HPJKPJ4P"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();