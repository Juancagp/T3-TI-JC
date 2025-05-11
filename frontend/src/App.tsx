import { useState } from "react";
import "./App.css";

interface Message {
  role: "user" | "system";
  content: string;
  loading?: boolean;
}

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "system", content: "Por favor, ingresa el link de un artículo de Wikipedia en inglés." },
  ]);
  const [articleLoaded, setArticleLoaded] = useState(false);

  const handleSubmit = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setMessages(prev => [...prev, { role: "user", content: trimmed }]);
    setInput("");

    // FASE 1: Subida de artículo
    if (!articleLoaded) {
      if (!/^https:\/\/en\.wikipedia\.org\/wiki\/.+/.test(trimmed)) {
        setMessages(prev => [
          ...prev,
          {
            role: "system",
            content: "❌ El link debe ser un artículo válido de Wikipedia en inglés (debe comenzar con https://en.wikipedia.org/wiki/...).",
          },
        ]);
        return;
      }

      setMessages(prev => [...prev, { role: "system", content: "Cargando artículo...", loading: true }]);

      try {
        const response = await fetch("http://localhost:8000/scrape", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: trimmed }),
        });

        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || "Error desconocido");
        }

        const data = await response.json();

        if (data.already_uploaded) {
          setMessages(prev => [
            ...prev.slice(0, -1),
            { role: "system", content: "ℹ️ Este artículo ya fue subido antes. Puedes hacer preguntas sobre él." },
          ]);
        } else {
          const preview = data.preview || "(sin preview)";
          setMessages(prev => [
            ...prev.slice(0, -1),
            { role: "system", content: "✅ Artículo cargado con éxito. Aquí un resumen:" },
            { role: "system", content: preview },
          ]);
        }

        setArticleLoaded(true);
      } catch (err: any) {
        setMessages(prev => [
          ...prev.slice(0, -1),
          { role: "system", content: `❌ Error al cargar el artículo: ${err.message}` },
          { role: "system", content: "Por favor, intenta subir otro link válido de Wikipedia." },
        ]);
        setArticleLoaded(false);
      }

      return;
    }

    // FASE 2: Preguntas al artículo cargado
    setMessages(prev => [
      ...prev,
      { role: "system", content: "🔍 Procesando tu consulta...", loading: true },
    ]);

    try {
      const response = await fetch("http://localhost:8000/askllm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed, top_k: 5 }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Error desconocido");
      }

      const data = await response.json();

      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: "system", content: `📘 ${data.answer}` },
      ]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: "system", content: "❌ Hubo un error procesando tu consulta." },
        { role: "system", content: `Detalles: ${err.message}` },
      ]);
    }
  };

  return (
    <div className="chat-container">
      <h1>AskAll - Powered by Wikipedia</h1>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`${msg.role} ${msg.loading ? "loading" : ""}`}>
            {msg.content}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          placeholder={
            articleLoaded ? "Haz una pregunta sobre el artículo..." : "Pega un link de Wikipedia..."
          }
          value={input}
          onChange={e => setInput(e.target.value)}
        />
        <button onClick={handleSubmit}>Enviar</button>
      </div>

      {articleLoaded && (
        <button
          className="reset-button"
          onClick={() => {
            setArticleLoaded(false);
            setMessages([
              { role: "system", content: "Por favor, ingresa el link de un artículo de Wikipedia en inglés." },
            ]);
          }}
        >
          🔄 Subir otro artículo
        </button>
      )}
    </div>
  );
}

export default App;
