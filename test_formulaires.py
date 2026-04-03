#!/usr/bin/env python
"""
Test simple pour vérifier que les formulaires s'initialisent correctement
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.forms import DepenseFeuilleDirectForm, DepenseFeuilleWorkflowForm, DepenseFeuilleForm

def test_formulaires():
    """Test que tous les formulaires s'initialisent sans erreur"""
    print("🧪 Test d'initialisation des formulaires")
    print("=" * 50)
    
    try:
        # Test formulaire de base
        print("1. Test DepenseFeuilleForm...")
        form_base = DepenseFeuilleForm()
        print(f"   ✅ Champs : {list(form_base.fields.keys())}")
        
        # Test formulaire direct
        print("2. Test DepenseFeuilleDirectForm...")
        form_direct = DepenseFeuilleDirectForm()
        print(f"   ✅ Champs : {list(form_direct.fields.keys())}")
        
        # Test formulaire workflow
        print("3. Test DepenseFeuilleWorkflowForm...")
        form_workflow = DepenseFeuilleWorkflowForm()
        print(f"   ✅ Champs : {list(form_workflow.fields.keys())}")
        
        # Vérification des champs workflow
        workflow_fields = ['releve_depense', 'demande', 'paiement_par', 'beneficiaire', 'date_paiement']
        
        print("\n📊 Analyse des champs :")
        print(f"   Formulaire base a les champs workflow : {all(field in form_base.fields for field in workflow_fields)}")
        print(f"   Formulaire direct cache les champs workflow : {not any(field in form_direct.fields for field in workflow_fields)}")
        print(f"   Formulaire workflow a les champs workflow : {all(field in form_workflow.fields for field in workflow_fields)}")
        
        print("\n🎉 Tous les formulaires s'initialisent correctement !")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_formulaires()
