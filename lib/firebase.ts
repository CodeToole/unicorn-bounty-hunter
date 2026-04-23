import { initializeApp, getApps, getApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAnalytics, isSupported } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyAc0IMvwr-Tn61xsWX_8hyndd2SMPeBcac",
  authDomain: "ubh-ecosystem-2026-30664.firebaseapp.com",
  projectId: "ubh-ecosystem-2026-30664",
  storageBucket: "ubh-ecosystem-2026-30664.firebasestorage.app",
  messagingSenderId: "1069062771368",
  appId: "1:1069062771368:web:8c0ca416d7e1d928d0a89d",
  measurementId: "G-11BDSDXVWZ"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const db = getFirestore(app);

let analytics;
if (typeof window !== "undefined") {
  isSupported().then((yes) => yes && (analytics = getAnalytics(app)));
}

export { db, analytics };
