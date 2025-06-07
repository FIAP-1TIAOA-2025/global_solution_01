# dashboard_app.py

from flask import Flask, render_template_string
from datetime import datetime
from src.prediction_api import predict_flood

app = Flask(__name__)

# HTML content for the dashboard
# Uses Tailwind CSS for styling and Inter font
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerta de Inundações - Porto Alegre</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts - Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5; /* Light gray background */
        }
        /* Custom styles for flood status based on risk level */
        .low-risk {
            background-color: #d1fae5; /* Green-100 */
            color: #065f46; /* Green-800 */
        }
        .moderate-risk {
            background-color: #fef3c7; /* Yellow-100 */
            color: #92400e; /* Yellow-800 */
        }
        .high-risk {
            background-color: #fee2e2; /* Red-100 */
            color: #991b1b; /* Red-800 */
        }
        .critical-risk {
            background-color: #fecaca; /* Red-200 */
            color: #dc2626; /* Red-700 */
            animation: pulse-red 1.5s infinite; /* Add pulsing animation */
        }
        @keyframes pulse-red {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.02); opacity: 0.9; }
        }
    </style>
</head>
<body class="flex flex-col min-h-screen items-center justify-center p-4">

    <div class="bg-white shadow-xl rounded-xl p-8 max-w-md w-full text-center space-y-6">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">
            Alerta de Inundações
        </h1>
        
        <div class="text-2xl font-semibold text-gray-700">
            Cidade: <span class="text-blue-600">Porto Alegre</span>
        </div>

        <div class="text-xl text-gray-600">
            Data e Hora Atuais: <span id="current-datetime" class="font-medium text-gray-800"></span>
        </div>

        <div class="p-6 rounded-lg shadow-md transition-colors duration-500" id="flood-status-card">
            <p class="text-xl font-semibold text-gray-700 mb-2">Possibilidade de Inundações:</p>
            <p id="flood-possibility" class="text-3xl font-extrabold"></p>
            <p class="text-sm text-gray-500 mt-2">
                (Simulação: O risco se atualiza aleatoriamente a cada 5 segundos. Em um sistema real, seria baseado em dados e modelos de ML.)
            </p>
        </div>

        <div class="text-sm text-gray-500 mt-4">
            Última atualização da simulação: <span id="last-sim-update"></span>
        </div>
    </div>

    <script>
        
        function updateDateTime() {
            const now = new Date();
            const options = {
                year: 'numeric', month: 'long', day: 'numeric',
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false
            };
            document.getElementById('current-datetime').textContent = now.toLocaleDateString('pt-BR', options);
        }

        const riskLevels = [
            { text: "Risco Baixo", class: "low-risk" },
            { text: "Risco Moderado", class: "moderate-risk" },
            { text: "Risco Alto", class: "high-risk" },
            { text: "RISCO CRÍTICO!", class: "critical-risk" }
        ];

        function updateFloodPossibility() {
            // In a real application, this would fetch data from your ML model API
            // For this simulation, we'll pick a random risk level
            const randomIndex = Math.floor(Math.random() * riskLevels.length);
            const selectedRisk = riskLevels[randomIndex];

            const floodPossibilityElement = document.getElementById('flood-possibility');
            const floodStatusCard = document.getElementById('flood-status-card');
            const lastSimUpdateElement = document.getElementById('last-sim-update');

            floodPossibilityElement.textContent = selectedRisk.text;

            // Remove all existing risk classes
            riskLevels.forEach(level => floodStatusCard.classList.remove(level.class));
            
            // Add the selected risk class
            floodStatusCard.classList.add(selectedRisk.class);

            // Update simulation timestamp
            const now = new Date();
            const options = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
            lastSimUpdateElement.textContent = now.toLocaleTimeString('pt-BR', options);
        }

        // Update date/time every second
        setInterval(updateDateTime, 1000);
        // Update flood possibility every 5 seconds (simulation)
        setInterval(updateFloodPossibility, 5000);

        // Initial calls to display content immediately on load
        updateDateTime();
        updateFloodPossibility();
    </script>

</body>
</html>
"""

@app.route('/')
def dashboard():    
    """
    Renders the flood alert dashboard web page.
    """
    return render_template_string(DASHBOARD_HTML)

if __name__ == '__main__':
    # To run the Flask app:
    # 1. Save this code as dashboard_app.py
    # 2. Open your terminal in the same directory as the file.
    # 3. Run: python dashboard_app.py
    # 4. Open your browser and go to http://127.0.0.1:5000/

    # For a production environment, use a WSGI server like Gunicorn or uWSGI.
    # For development, debug=True provides useful error messages and auto-reloads.
    app.run(debug=True, host='0.0.0.0', port=3000)