from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import sys
import os

# Add parent directory to path to import utilidades
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utilidades as herramientas

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache for races list
races_cache = None

@app.route('/api/races', methods=['GET'])
def get_races():
    """Get list of available races"""
    global races_cache
    
    try:
        # Load races if not cached
        if races_cache is None:
            df_carreras = herramientas.cargar_lista_carreras()
            if df_carreras is not None and not df_carreras.empty:
                races_cache = df_carreras.to_dict('records')
            else:
                races_cache = []
        
        return jsonify({
            'success': True,
            'races': races_cache
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/results', methods=['POST'])
def get_results():
    """Get results for a specific race"""
    try:
        data = request.get_json()
        race_url = data.get('url')
        
        print(f"\n{'='*60}")
        print(f"📥 Received request for race: {race_url}")
        print(f"{'='*60}")
        
        if not race_url:
            print("❌ Error: No race URL provided")
            return jsonify({
                'success': False,
                'error': 'Race URL is required'
            }), 400
        
        # Extract the slug from the URL (remove the base URL part)
        # The URL format is like: "race/gp-d-ouverture/2026"
        slug = race_url
        
        print(f"🔍 Searching for results with slug: {slug}")
        
        # Get results using utilidades
        df_results = herramientas.buscar_resultados_carrera(slug)
        
        if df_results is None or df_results.empty:
            print(f"⚠️  No results found for: {slug}")
            print(f"💡 Tip: This race may not have results yet (future race) or the URL may be incorrect")
            return jsonify({
                'success': False,
                'error': 'No results found for this race. This may be a future race or the data is not available yet.'
            }), 404
        
        # Convert DataFrame to list of dictionaries
        results = df_results.to_dict('records')
        
        print(f"✅ Successfully retrieved {len(results)} results")
        print(f"📊 Sample data: {results[0] if results else 'No data'}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        print(f"❌ Error getting results: {e}")
        print(f"🔧 Exception type: {type(e).__name__}")
        import traceback
        print(f"📋 Traceback:\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Cycling Race Viewer API is running'
    })

if __name__ == '__main__':
    print("Starting Cycling Race Viewer API...")
    print("API will be available at: http://localhost:5000")
    print("Access the web interface by opening web_carreras/index.html in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
