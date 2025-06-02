import './App.css'
import { signInWithGoogle } from './firebase/firebase' 

function App() {
  return (
    <div className="p-4">
      <button
        onClick={signInWithGoogle}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
      >
        Sign in with Google
      </button>
    </div>
  );
}

export default App;
