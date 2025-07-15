import streamlit as st
import requests
import datetime
import pytz
from dateutil import parser

st.title("Résumé quotidien Limitless")

# Récupère les clés API depuis les secrets Streamlit Cloud
api_key = st.secrets.get("LIMITLESS_API_KEY", "")
openai_key = st.secrets.get("OPENAI_API_KEY", "")

date = st.date_input("Date du résumé", datetime.date.today())
timezone = st.text_input("Fuseau horaire (ex: Europe/Paris)", value="Europe/Paris")

if st.button("Générer mon résumé quotidien"):
    if not api_key:
        st.error("Merci de renseigner ta clé API Limitless (Settings > Secrets sur Streamlit Cloud).")
    else:
        url = "https://api.limitless.ai/v1/lifelogs"
        headers = {"X-API-Key": api_key}
        params = {
            "date": date.isoformat(),
            "timezone": timezone,
            "includeMarkdown": "true",
            "includeHeadings": "true",
            "limit": 10
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                lifelogs = data.get("data", {}).get("lifelogs", [])
                if not lifelogs:
                    st.info("Aucun lifelog trouvé pour cette date.")
                else:
                    # On limite à 10000 caractères pour ne pas dépasser la limite OpenAI
                    full_text = "\n\n".join([log.get("markdown", "") for log in lifelogs])
                    if len(full_text) > 10000:
                        full_text = full_text[:10000] + "\n\n[Texte tronqué pour respecter la limite OpenAI]"
                    st.subheader("Résumé structuré en 10 points :")
                    if not openai_key:
                        st.warning("Merci de renseigner ta clé OpenAI (Settings > Secrets sur Streamlit Cloud).")
                    else:
                        openai_url = "https://api.openai.com/v1/chat/completions"
                        headers_oa = {
                            "Authorization": f"Bearer {openai_key}",
                            "Content-Type": "application/json"
                        }
                        prompt = (
                            "Voici le journal de ma journée. Résume-le en exactement 10 bullet points clairs, synthétiques, numérotés de 1 à 10, en français, sans rien inventer, même si certains points sont courts :\n"
                            + full_text
                        )
                        payload = {
                            "model": "gpt-3.5-turbo",
                            "messages": [
                                {"role": "system", "content": "Tu es un assistant qui résume des journées de façon concise et structurée."},
                                {"role": "user", "content": prompt}
                            ],
                            "max_tokens": 500,
                            "temperature": 0.5
                        }
                        try:
                            res_oa = requests.post(openai_url, headers=headers_oa, json=payload)
                            if res_oa.status_code == 200:
                                summary = res_oa.json()["choices"][0]["message"]["content"]
                                st.markdown(summary)
                                st.info("Résumé généré par OpenAI.")
                            else:
                                st.error(f"Erreur OpenAI : {res_oa.status_code} - {res_oa.text}")
                        except Exception as e:
                            st.error(f"Erreur lors de la requête OpenAI : {e}")
                    st.markdown("---")
                    st.subheader("Détail des lifelogs :")
                    paris_tz = pytz.timezone("Europe/Paris")
                    for log in lifelogs:
                        # Conversion et affichage des horaires en heure française 24h
                        start = log.get("startTime")
                        end = log.get("endTime")
                        try:
                            if start:
                                start_dt = parser.isoparse(start).astimezone(paris_tz)
                                start_str = start_dt.strftime("%H:%M")
                            else:
                                start_str = "?"
                            if end:
                                end_dt = parser.isoparse(end).astimezone(paris_tz)
                                end_str = end_dt.strftime("%H:%M")
                            else:
                                end_str = "?"
                        except Exception:
                            start_str = end_str = "?"
                        st.markdown(f"**[{start_str} - {end_str}] {log.get('title', 'Sans titre')}**")
                        st.write(log.get("markdown", ""))
            else:
                st.error(f"Erreur API : {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Erreur lors de la requête : {e}")