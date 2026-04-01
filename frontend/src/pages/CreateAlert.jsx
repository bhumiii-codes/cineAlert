import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";

const API = "http://localhost:5000";

const CITIES = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Kolkata"];
const FORMATS = ["2D", "3D", "IMAX"];
const TIMES = ["Morning", "Afternoon", "Evening", "Night"];

export default function CreateAlert() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [movie, setMovie] = useState("");
  const [city, setCity] = useState("");
  const [formats, setFormats] = useState([]);
  const [times, setTimes] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  const toggleItem = (item, list, setList) => {
    setList(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      // Register user first (in case they're new)
      await axios.post(`${API}/users`, {
        telegram_id: user.uid,
        name: user.displayName,
      });

      // Create one alert per format+time combination
      for (const fmt of formats) {
        for (const time of times.length > 0 ? times : ["ANY"]) {
          await axios.post(`${API}/alerts`, {
            telegram_id: user.uid,
            movie_name: movie,
            city: city,
            format: fmt,
            preferred_time: time.toUpperCase(),
            venue: "ANY",
          });
        }
      }
      navigate("/dashboard");
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-md">

        {/* Back button */}
        <button
          onClick={() => step === 1 ? navigate("/dashboard") : setStep(step - 1)}
          className="text-gray-400 hover:text-white mb-6 flex items-center gap-2 transition"
        >
          ← Back
        </button>

        {/* Progress */}
        <div className="flex gap-2 mb-8">
          {[1, 2, 3, 4].map(s => (
            <div key={s} className={`h-1 flex-1 rounded-full transition-all ${
              s <= step ? "bg-indigo-500" : "bg-gray-800"
            }`} />
          ))}
        </div>

        {/* Step 1 — Movie */}
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">Which movie?</h2>
            <p className="text-gray-400 mb-6">Type the name of the movie you want to watch</p>
            <input
              type="text"
              value={movie}
              onChange={e => setMovie(e.target.value)}
              placeholder="e.g. Project Hail Mary"
              className="w-full bg-gray-900 border border-gray-700 rounded-2xl px-4 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-lg"
            />
            <button
              onClick={() => setStep(2)}
              disabled={!movie.trim()}
              className="w-full mt-6 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition rounded-2xl py-4 font-semibold text-lg"
            >
              Next →
            </button>
          </div>
        )}

        {/* Step 2 — City */}
        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">Which city?</h2>
            <p className="text-gray-400 mb-6">Pick the city you want to watch it in</p>
            <div className="grid grid-cols-2 gap-3">
              {CITIES.map(c => (
                <button
                  key={c}
                  onClick={() => setCity(c)}
                  className={`py-4 rounded-2xl font-medium transition ${
                    city === c
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-900 text-gray-300 hover:bg-gray-800"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
            <button
              onClick={() => setStep(3)}
              disabled={!city}
              className="w-full mt-6 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition rounded-2xl py-4 font-semibold text-lg"
            >
              Next →
            </button>
          </div>
        )}

        {/* Step 3 — Format */}
        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">Which format?</h2>
            <p className="text-gray-400 mb-6">Select all formats you're okay with</p>
            <div className="flex flex-col gap-3">
              {FORMATS.map(f => (
                <button
                  key={f}
                  onClick={() => toggleItem(f, formats, setFormats)}
                  className={`py-4 rounded-2xl font-medium transition flex items-center justify-between px-5 ${
                    formats.includes(f)
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-900 text-gray-300 hover:bg-gray-800"
                  }`}
                >
                  <span>{f}</span>
                  {formats.includes(f) && <span>✓</span>}
                </button>
              ))}
            </div>
            <button
              onClick={() => setStep(4)}
              disabled={formats.length === 0}
              className="w-full mt-6 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition rounded-2xl py-4 font-semibold text-lg"
            >
              Next →
            </button>
          </div>
        )}

        {/* Step 4 — Time */}
        {step === 4 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">Preferred timing?</h2>
            <p className="text-gray-400 mb-6">Select all time slots that work for you (or skip for any time)</p>
            <div className="grid grid-cols-2 gap-3">
              {TIMES.map(t => (
                <button
                  key={t}
                  onClick={() => toggleItem(t, times, setTimes)}
                  className={`py-4 rounded-2xl font-medium transition ${
                    times.includes(t)
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-900 text-gray-300 hover:bg-gray-800"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="w-full mt-6 bg-green-600 hover:bg-green-500 disabled:opacity-40 transition rounded-2xl py-4 font-semibold text-lg"
            >
              {submitting ? "Creating..." : "🔔 Create Alert"}
            </button>
          </div>
        )}

      </div>
    </div>
  );
}