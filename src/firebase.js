// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore"; // Import Firestore
import { getDatabase } from "firebase/database"; // Import Realtime Database if needed
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDlOQiLRAM3KGpGcQq_K0udEKGztXsHiS8",
  authDomain: "cuentacuentos-d3e36.firebaseapp.com",
  projectId: "cuentacuentos-d3e36",
  storageBucket: "cuentacuentos-d3e36.appspot.com",
  messagingSenderId: "404706405593",
  appId: "1:404706405593:web:ef04e565e4b5bc98ae22c8",
  measurementId: "G-8ZKXBVW9XV"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getFirestore(app); // Initialize Firestore
const realtimeDb = getDatabase(app); // Initialize Realtime Database if needed

export { db, realtimeDb };
