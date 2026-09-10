import { useState } from "react";


function App() {

  const [description, setDescription] = useState("");

  const [requirements, setRequirements] = useState(null);

  const [loading, setLoading] = useState(false);


  const handleSubmit = async () => {

    if (!description.trim()) {
      return;
    }


    setLoading(true);


    try {

      const response = await fetch(

        "http://127.0.0.1:8000/building/analyze",

        {

          method: "POST",

          headers: {

            "Content-Type": "application/json"

          },

          body: JSON.stringify({

            description: description

          })

        }

      );


      const data = await response.json();


      setRequirements(
        data.requirements
      );


    } catch (error) {

      console.error(error);

    }


    setLoading(false);

  };


  return (

    <div>

      <h1>
        ArchFlow AI
      </h1>


      <p>
        Tell us about the building you want to create.
      </p>


      <textarea

        value={description}

        onChange={(event) =>

          setDescription(event.target.value)

        }

        placeholder="Example: I want a modern house for five people"

        rows="6"

        cols="60"

      />


      <br />


      <button

        onClick={handleSubmit}

        disabled={loading}

      >

        {loading
          ? "Analyzing..."
          : "Analyze Requirements"
        }

      </button>


      {requirements && (

        <div>

          <h2>
            Extracted Requirements
          </h2>


          <pre>

            {JSON.stringify(
              requirements,
              null,
              2
            )}

          </pre>

        </div>

      )}

    </div>

  );

}


export default App;