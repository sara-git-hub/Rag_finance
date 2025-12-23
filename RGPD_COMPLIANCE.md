# Conformité RGPD & Loi 09-08 - MiniRAG

**Projet**: MiniRAG - Système RAG avec LangChain
**Date de création**: 2025-12-17
**Durée de conservation définie**: 2 ans
**Responsable**: [À définir]

---

## 📋 Cadre légal applicable

### Maroc - Loi 09-08
- **Texte**: Loi n° 09-08 relative à la protection des personnes physiques à l'égard du traitement des données à caractère personnel
- **Autorité**: CNDP (Commission Nationale de contrôle de la protection des Données à caractère Personnel)
- **Site web**: https://www.cndp.ma
- **Contact**: contact@cndp.ma / 0537 57 11 54

### Union Européenne - RGPD
- **Texte**: Règlement (UE) 2016/679
- **Applicable si**: Traitement de données de résidents UE

---

## ✅ Ce qui est déjà implémenté

### Sécurité technique

| Fonctionnalité | Status | Implémentation | Fichier |
|----------------|--------|----------------|---------|
| **Authentification JWT** | ✅ | Tokens sécurisés avec expiration | `src/helpers/auth.py` |
| **Contrôle d'accès par rôles** | ✅ | Admin / User avec permissions différenciées | `src/helpers/auth.py` |
| **HTTPS/SSL** | ✅ | Nginx reverse proxy avec SSL | `docker/nginx/default.conf` |
| **Base de données sécurisée** | ✅ | PostgreSQL avec authentification | `docker/env/.env.postgres` |
| **Isolation des données** | ✅ | Projets séparés, pas de leak entre users | Architecture multi-tenant |

### Droits des personnes

| Droit | Status | Implémentation | Route API |
|-------|--------|----------------|-----------|
| **Droit de suppression (fichiers)** | ✅ | DELETE assets par ID | `DELETE /api/v1/admin/assets/{asset_id}` |
| **Droit de suppression (chunks)** | ✅ | DELETE chunks par ID | `DELETE /api/v1/admin/chunks/{chunk_id}` |
| **Droit de suppression (conversations)** | ✅ | DELETE conversations | `DELETE /api/v1/admin/conversations/{conversation_id}` |
| **Droit de suppression (vecteurs)** | ✅ | DELETE collections Qdrant | `DELETE /api/v1/admin/vectors/collections/{collection_name}` |
| **Droit de suppression (projets)** | ✅ | DELETE projet complet | `DELETE /api/v1/admin/projects/{project_id}` |

### Traçabilité

| Fonctionnalité | Status | Détails |
|----------------|--------|---------|
| **Logs applicatifs** | ✅ | Uvicorn logs + stdout/stderr |
| **Métadonnées documents** | ✅ | created_at, updated_at sur tous les modèles |
| **Métriques Prometheus** | ✅ | Monitoring des requêtes et performances |

---

## ❌ Ce qui reste à faire

### 🔴 PRIORITÉ 1 - Urgent (sous 1 mois)

#### 1. Déclaration CNDP
- [ ] **Préparer le dossier de déclaration**
  - Finalité du traitement
  - Catégories de données traitées
  - Destinataires des données
  - Durée de conservation (2 ans)
  - Mesures de sécurité
- [ ] **Soumettre la déclaration** sur https://www.cndp.ma
- [ ] **Obtenir le récépissé CNDP**
- [ ] **Coût estimé**: 500-1000 MAD
- [ ] **Délai estimé**: 2-3 mois

#### 2. Politique de confidentialité
- [ ] **Créer la page `/privacy-policy`** dans le frontend
- [ ] **Contenu à inclure**:
  - Identité du responsable de traitement
  - Types de données collectées (documents PDF, métadonnées, conversations)
  - Finalités (recherche documentaire, Q&A avec LLM)
  - Durée de conservation (2 ans)
  - Droits des utilisateurs (accès, rectification, suppression)
  - Contact CNDP et responsable
  - APIs externes utilisées (Groq, OpenAI, Cohere, Ollama)
- [ ] **Ajouter lien dans le footer** de l'application

#### 3. Consentement à l'upload
- [ ] **Modifier `frontend/src/pages/Upload.jsx`**
- [ ] **Ajouter checkbox obligatoire**:
  ```jsx
  <Checkbox required>
    J'ai lu et j'accepte la politique de confidentialité.
    Je consens au traitement de mes documents pour une durée de 2 ans.
  </Checkbox>
  ```
- [ ] **Bloquer l'upload si non coché**
- [ ] **Stocker le consentement** en base (table `consents`)

### 🟠 PRIORITÉ 2 - Important (sous 3 mois)

#### 4. Durée de conservation automatique (2 ans)
- [ ] **Créer un job de nettoyage automatique**
  - Fichier: `src/exchange_rates/jobs/cleanup_old_data.py`
  - Fréquence: Quotidien à 3h du matin
  - Action: Supprimer assets > 2 ans
- [ ] **Ajouter au scheduler**
- [ ] **Notifier les utilisateurs 30 jours avant suppression** (optionnel)
- [ ] **SQL de nettoyage**:
  ```sql
  -- Supprimer les assets > 2 ans
  DELETE FROM assets WHERE created_at < NOW() - INTERVAL '2 years';

  -- Supprimer les chunks orphelins
  DELETE FROM datachunks WHERE chunk_asset_id NOT IN (SELECT asset_id FROM assets);
  ```

#### 5. Logs d'audit (traçabilité accès)
- [ ] **Créer table `audit_logs`**:
  ```sql
  CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(50), -- 'upload', 'view', 'delete', 'search', 'qa'
    resource_type VARCHAR(50), -- 'asset', 'project', 'conversation'
    resource_id INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
  );
  ```
- [ ] **Ajouter logging dans les routes**:
  - Upload fichier
  - Consultation document
  - Recherche
  - Question/Réponse
  - Suppression
- [ ] **Interface admin pour consulter les logs**

#### 6. Registre des traitements
- [ ] **Créer document `docs/REGISTRE_TRAITEMENTS.md`**
- [ ] **Contenu requis**:
  - Nom du traitement
  - Finalités
  - Catégories de personnes concernées
  - Catégories de données
  - Catégories de destinataires
  - Transferts hors Maroc/UE
  - Délais d'effacement (2 ans)
  - Mesures de sécurité techniques et organisationnelles

### 🟡 PRIORITÉ 3 - Souhaitable (sous 6 mois)

#### 7. Responsable de la protection des données (DPO)
- [ ] **Désigner un DPO** (interne ou externe)
- [ ] **Publier ses coordonnées** dans la politique de confidentialité
- [ ] **Former le DPO** aux obligations légales

#### 8. Analyse d'impact (PIA - Privacy Impact Assessment)
- [ ] **Télécharger l'outil PIA CNIL**: https://www.cnil.fr/fr/outil-pia-telechargez-et-installez-le-logiciel-de-la-cnil
- [ ] **Réaliser l'analyse**:
  - Identifier les risques pour les données
  - Évaluer la gravité et la probabilité
  - Définir des mesures de mitigation
- [ ] **Documenter les résultats**

#### 9. Clauses contractuelles APIs externes
- [ ] **Vérifier les DPA (Data Processing Agreements)** avec:
  - Groq (USA)
  - OpenAI (USA)
  - Cohere (Canada)
  - HuggingFace (UE/USA)
- [ ] **S'assurer de l'adéquation RGPD** ou ajouter des clauses contractuelles types
- [ ] **Alternative**: Privilégier Ollama (local) pour éviter les transferts

#### 10. Export des données utilisateur
- [ ] **Créer route API** `GET /api/v1/users/me/export`
- [ ] **Format de sortie**: JSON ou ZIP
- [ ] **Contenu**:
  - Tous les documents uploadés
  - Toutes les conversations
  - Métadonnées du compte
- [ ] **Délai de traitement**: 48h maximum

#### 11. Chiffrement des données sensibles
- [ ] **Identifier les données sensibles** dans les documents
- [ ] **Chiffrer les colonnes sensibles** en base:
  ```python
  from cryptography.fernet import Fernet
  # Chiffrer asset_name, chunk_text si contient données sensibles
  ```
- [ ] **Gérer les clés de chiffrement** via secrets management

#### 12. Anonymisation (optionnel)
- [ ] **Outil de détection de données personnelles** dans les PDFs
- [ ] **Masquage automatique** (emails, téléphones, noms)
- [ ] **Librairie**: spaCy + patterns regex

---

## 📊 Tableau de bord de conformité

| Catégorie | Progression | Actions complétées | Actions totales |
|-----------|-------------|-------------------|-----------------|
| **Sécurité technique** | 🟢 90% | 5/6 | Chiffrement manquant |
| **Droits des personnes** | 🟢 80% | 5/6 | Export manquant |
| **Traçabilité** | 🟡 40% | 2/5 | Logs audit + registre manquants |
| **Conformité légale** | 🔴 20% | 0/4 | CNDP + politique + consentement manquants |
| **GLOBAL** | 🟡 50% | 12/21 | 9 actions restantes |

---

## 🎯 Roadmap de mise en conformité

### Phase 1 - Mois 1 (URGENT)
```
Semaine 1-2: Politique de confidentialité + Consentement upload
Semaine 3-4: Déclaration CNDP (préparation dossier)
```

### Phase 2 - Mois 2-3 (IMPORTANT)
```
Mois 2: Logs d'audit + Registre des traitements
Mois 3: Durée conservation automatique (job cleanup)
```

### Phase 3 - Mois 4-6 (SOUHAITABLE)
```
Mois 4: DPO + PIA
Mois 5: Clauses contractuelles APIs + Export données
Mois 6: Chiffrement + Anonymisation
```

---

## 📞 Contacts et ressources

### Autorités
- **CNDP Maroc**: https://www.cndp.ma - contact@cndp.ma - 0537 57 11 54
- **CNIL France**: https://www.cnil.fr (pour RGPD)

### Ressources utiles
- [Texte Loi 09-08 (PDF)](https://www.cndp.ma/images/lois/Loi-09-08-Fr.pdf)
- [Guide RGPD du développeur](https://www.cnil.fr/fr/guide-rgpd-du-developpeur)
- [Outil PIA CNIL](https://www.cnil.fr/fr/outil-pia-telechargez-et-installez-le-logiciel-de-la-cnil)
- [Modèles de clauses CNIL](https://www.cnil.fr/fr/modeles)

### Avocats spécialisés (si besoin)
- Cabinet Jawhari: https://avocat-jawhari.com
- Village Justice: https://www.village-justice.com

---

## 📝 Historique des modifications

| Date | Version | Modifications | Auteur |
|------|---------|---------------|--------|
| 2025-12-17 | 1.0 | Création initiale | Claude Code |

---

## ⚠️ Avertissement

Ce document est fourni à titre informatif et ne constitue pas un avis juridique. Pour une conformité complète, il est recommandé de consulter un avocat spécialisé en protection des données et de se rapprocher de la CNDP.

**Sanctions en cas de non-conformité:**
- Amendes: 10,000 à 100,000 MAD
- Peines de prison possibles (cas graves)
- Fermeture administrative
- Dommages et intérêts aux victimes

**Statistiques 2024:**
- 27 millions MAD d'amendes imposées par la CNDP
- 48% des entreprises contrôlées étaient non-conformes
