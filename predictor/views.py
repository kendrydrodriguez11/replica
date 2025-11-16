from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os
import tempfile
from .services import StockPredictor

def index(request):
    return render(request, 'predictor/index.html')

@csrf_exempt
def predict_stock(request):
    if request.method == 'POST':
        try:
            # Validar archivo
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'success': False, 'error': 'No se proporcionó archivo'}, status=400)
            
            # Validar extensión
            if not uploaded_file.name.endswith('.csv'):
                return JsonResponse({'success': False, 'error': 'Solo se aceptan archivos CSV'}, status=400)
            
            # Crear directorio temporal si no existe
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Guardar archivo
            file_path = default_storage.save(f'tmp/{uploaded_file.name}', uploaded_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Parsear parámetros
            params = json.loads(request.POST.get('params', '{}'))
            n_test = int(params.get('n_test', 300))
            epochs = int(params.get('epochs', 100))
            hidden_dim = int(params.get('hidden_dim', 16))
            n_layers = int(params.get('n_layers', 2))
            lr = float(params.get('lr', 0.01))
            
            # Preparar datos
            data = StockPredictor.prepare_data(full_path, n_test)
            
            # Crear y entrenar predictor
            predictor = StockPredictor(
                hidden_dim=hidden_dim,
                n_layers=n_layers,
                lr=lr,
                epochs=epochs
            )
            
            # Realizar predicciones
            predictions = predictor.train_and_predict(
                data['trainX'],
                data['trainy'],
                data['testX']
            )
            
            # Reconstruir precios
            predicted_prices = StockPredictor.reconstruct_prices(
                predictions,
                data['close_prices'],
                n_test
            )
            
            # Obtener datos reales
            actual_prices = data['close_prices'][-n_test:].tolist()
            dates = data['dates'][-n_test:].dt.strftime('%Y-%m-%d').tolist()
            
            # Calcular métricas
            metrics = StockPredictor.calculate_metrics(actual_prices, predicted_prices)
            
            # Limpiar archivo temporal
            try:
                default_storage.delete(file_path)
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'dates': dates,
                'actual_prices': actual_prices,
                'predicted_prices': predicted_prices,
                'metrics': metrics
            })
            
        except FileNotFoundError as e:
            return JsonResponse({'success': False, 'error': f'Archivo no encontrado: {str(e)}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f'Error en formato JSON: {str(e)}'}, status=400)
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error detallado: {error_detail}")  # Para debugging
            return JsonResponse({'success': False, 'error': f'Error: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)