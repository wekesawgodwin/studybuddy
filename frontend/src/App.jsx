import { useState, useEffect } from "react"

function App() {
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL
    console.log("1. API URL is:", apiUrl)

    fetch(`${apiUrl}/hello`)
      .then((res) => {
        console.log("2. Response status:", res.status)
        console.log("3. Response ok:", res.ok)
        return res.json()
      })
      .then((data) => {
        console.log("4. Data received:", data)
        console.log("5. data.message is:", data.message)
        setMessage(data.message)
        setLoading(false)
      })
      .catch((err) => {
        console.log("6. Error caught:", err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  console.log("7. Current state — loading:", loading, "message:", message, "error:", error)

  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error}</p>

  return (
    <div>
      <h1>{message}</h1>
    </div>
  )
}

export default App