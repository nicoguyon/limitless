<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta http-equiv="Content-Style-Type" content="text/css">
  <title></title>
  <meta name="Generator" content="Cocoa HTML Writer">
  <meta name="CocoaVersion" content="2575.6">
  <style type="text/css">
    p.p1 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica}
    p.p2 {margin: 0.0px 0.0px 0.0px 0.0px; font: 12.0px Helvetica; min-height: 14.0px}
  </style>
</head>
<body>
<p class="p1">import streamlit as st</p>
<p class="p1">import requests</p>
<p class="p1">import datetime</p>
<p class="p1">import pytz</p>
<p class="p1">from dateutil import parser</p>
<p class="p2"><br></p>
<p class="p1">st.title("Résumé quotidien Limitless")</p>
<p class="p2"><br></p>
<p class="p1"># Récupère les clés API depuis les secrets Streamlit Cloud</p>
<p class="p1">api_key = st.secrets.get("LIMITLESS_API_KEY", "")</p>
<p class="p1">openai_key = st.secrets.get("OPENAI_API_KEY", "")</p>
<p class="p2"><br></p>
<p class="p1">date = st.date_input("Date du résumé", datetime.date.today())</p>
<p class="p1">timezone = st.text_input("Fuseau horaire (ex: Europe/Paris)", value="Europe/Paris")</p>
<p class="p2"><br></p>
<p class="p1">if st.button("Générer mon résumé quotidien"):</p>
<p class="p1"><span class="Apple-converted-space">    </span>if not api_key:</p>
<p class="p1"><span class="Apple-converted-space">        </span>st.error("Merci de renseigner ta clé API Limitless (Settings &gt; Secrets sur Streamlit Cloud).")</p>
<p class="p1"><span class="Apple-converted-space">    </span>else:</p>
<p class="p1"><span class="Apple-converted-space">        </span>url = "https://api.limitless.ai/v1/lifelogs"</p>
<p class="p1"><span class="Apple-converted-space">        </span>headers = {"X-API-Key": api_key}</p>
<p class="p1"><span class="Apple-converted-space">        </span>params = {</p>
<p class="p1"><span class="Apple-converted-space">            </span>"date": date.isoformat(),</p>
<p class="p1"><span class="Apple-converted-space">            </span>"timezone": timezone,</p>
<p class="p1"><span class="Apple-converted-space">            </span>"includeMarkdown": "true",</p>
<p class="p1"><span class="Apple-converted-space">            </span>"includeHeadings": "true",</p>
<p class="p1"><span class="Apple-converted-space">            </span>"limit": 10</p>
<p class="p1"><span class="Apple-converted-space">        </span>}</p>
<p class="p1"><span class="Apple-converted-space">        </span>try:</p>
<p class="p1"><span class="Apple-converted-space">            </span>response = requests.get(url, headers=headers, params=params)</p>
<p class="p1"><span class="Apple-converted-space">            </span>if response.status_code == 200:</p>
<p class="p1"><span class="Apple-converted-space">                </span>data = response.json()</p>
<p class="p1"><span class="Apple-converted-space">                </span>lifelogs = data.get("data", {}).get("lifelogs", [])</p>
<p class="p1"><span class="Apple-converted-space">                </span>if not lifelogs:</p>
<p class="p1"><span class="Apple-converted-space">                    </span>st.info("Aucun lifelog trouvé pour cette date.")</p>
<p class="p1"><span class="Apple-converted-space">                </span>else:</p>
<p class="p1"><span class="Apple-converted-space">                    </span># On limite à 10000 caractères pour ne pas dépasser la limite OpenAI</p>
<p class="p1"><span class="Apple-converted-space">                    </span>full_text = "\n\n".join([log.get("markdown", "") for log in lifelogs])</p>
<p class="p1"><span class="Apple-converted-space">                    </span>if len(full_text) &gt; 10000:</p>
<p class="p1"><span class="Apple-converted-space">                        </span>full_text = full_text[:10000] + "\n\n[Texte tronqué pour respecter la limite OpenAI]"</p>
<p class="p1"><span class="Apple-converted-space">                    </span>st.subheader("Résumé structuré en 10 points :")</p>
<p class="p1"><span class="Apple-converted-space">                    </span>if not openai_key:</p>
<p class="p1"><span class="Apple-converted-space">                        </span>st.warning("Merci de renseigner ta clé OpenAI (Settings &gt; Secrets sur Streamlit Cloud).")</p>
<p class="p1"><span class="Apple-converted-space">                    </span>else:</p>
<p class="p1"><span class="Apple-converted-space">                        </span>openai_url = "https://api.openai.com/v1/chat/completions"</p>
<p class="p1"><span class="Apple-converted-space">                        </span>headers_oa = {</p>
<p class="p1"><span class="Apple-converted-space">                            </span>"Authorization": f"Bearer {openai_key}",</p>
<p class="p1"><span class="Apple-converted-space">                            </span>"Content-Type": "application/json"</p>
<p class="p1"><span class="Apple-converted-space">                        </span>}</p>
<p class="p1"><span class="Apple-converted-space">                        </span>prompt = (</p>
<p class="p1"><span class="Apple-converted-space">                            </span>"Voici le journal de ma journée. Résume-le en exactement 10 bullet points clairs, synthétiques, numérotés de 1 à 10, en français, sans rien inventer, même si certains points sont courts :\n"</p>
<p class="p1"><span class="Apple-converted-space">                            </span>+ full_text</p>
<p class="p1"><span class="Apple-converted-space">                        </span>)</p>
<p class="p1"><span class="Apple-converted-space">                        </span>payload = {</p>
<p class="p1"><span class="Apple-converted-space">                            </span>"model": "gpt-3.5-turbo",</p>
<p class="p1"><span class="Apple-converted-space">                            </span>"messages": [</p>
<p class="p1"><span class="Apple-converted-space">                                </span>{"role": "system", "content": "Tu es un assistant qui résume des journées de façon concise et structurée."},</p>
<p class="p1"><span class="Apple-converted-space">                                </span>{"role": "user", "content": prompt}</p>
<p class="p1"><span class="Apple-converted-space">                            </span>],</p>
<p class="p1"><span class="Apple-converted-space">                            </span>"max_tokens": 500,</p>
<p class="p1"><span class="Apple-converted-space">                            </span>"temperature": 0.5</p>
<p class="p1"><span class="Apple-converted-space">                        </span>}</p>
<p class="p1"><span class="Apple-converted-space">                        </span>try:</p>
<p class="p1"><span class="Apple-converted-space">                            </span>res_oa = requests.post(openai_url, headers=headers_oa, json=payload)</p>
<p class="p1"><span class="Apple-converted-space">                            </span>if res_oa.status_code == 200:</p>
<p class="p1"><span class="Apple-converted-space">                                </span>summary = res_oa.json()["choices"][0]["message"]["content"]</p>
<p class="p1"><span class="Apple-converted-space">                                </span>st.markdown(summary)</p>
<p class="p1"><span class="Apple-converted-space">                                </span>st.info("Résumé généré par OpenAI.")</p>
<p class="p1"><span class="Apple-converted-space">                            </span>else:</p>
<p class="p1"><span class="Apple-converted-space">                                </span>st.error(f"Erreur OpenAI : {res_oa.status_code} - {res_oa.text}")</p>
<p class="p1"><span class="Apple-converted-space">                        </span>except Exception as e:</p>
<p class="p1"><span class="Apple-converted-space">                            </span>st.error(f"Erreur lors de la requête OpenAI : {e}")</p>
<p class="p1"><span class="Apple-converted-space">                    </span>st.markdown("---")</p>
<p class="p1"><span class="Apple-converted-space">                    </span>st.subheader("Détail des lifelogs :")</p>
<p class="p1"><span class="Apple-converted-space">                    </span>paris_tz = pytz.timezone("Europe/Paris")</p>
<p class="p1"><span class="Apple-converted-space">                    </span>for log in lifelogs:</p>
<p class="p1"><span class="Apple-converted-space">                        </span># Conversion et affichage des horaires en heure française 24h</p>
<p class="p1"><span class="Apple-converted-space">                        </span>start = log.get("startTime")</p>
<p class="p1"><span class="Apple-converted-space">                        </span>end = log.get("endTime")</p>
<p class="p1"><span class="Apple-converted-space">                        </span>try:</p>
<p class="p1"><span class="Apple-converted-space">                            </span>if start:</p>
<p class="p1"><span class="Apple-converted-space">                                </span>start_dt = parser.isoparse(start).astimezone(paris_tz)</p>
<p class="p1"><span class="Apple-converted-space">                                </span>start_str = start_dt.strftime("%H:%M")</p>
<p class="p1"><span class="Apple-converted-space">                            </span>else:</p>
<p class="p1"><span class="Apple-converted-space">                                </span>start_str = "?"</p>
<p class="p1"><span class="Apple-converted-space">                            </span>if end:</p>
<p class="p1"><span class="Apple-converted-space">                                </span>end_dt = parser.isoparse(end).astimezone(paris_tz)</p>
<p class="p1"><span class="Apple-converted-space">                                </span>end_str = end_dt.strftime("%H:%M")</p>
<p class="p1"><span class="Apple-converted-space">                            </span>else:</p>
<p class="p1"><span class="Apple-converted-space">                                </span>end_str = "?"</p>
<p class="p1"><span class="Apple-converted-space">                        </span>except Exception:</p>
<p class="p1"><span class="Apple-converted-space">                            </span>start_str = end_str = "?"</p>
<p class="p1"><span class="Apple-converted-space">                        </span>st.markdown(f"**[{start_str} - {end_str}] {log.get('title', 'Sans titre')}**")</p>
<p class="p1"><span class="Apple-converted-space">                        </span>st.write(log.get("markdown", ""))</p>
<p class="p1"><span class="Apple-converted-space">            </span>else:</p>
<p class="p1"><span class="Apple-converted-space">                </span>st.error(f"Erreur API : {response.status_code} - {response.text}")</p>
<p class="p1"><span class="Apple-converted-space">        </span>except Exception as e:</p>
<p class="p1"><span class="Apple-converted-space">            </span>st.error(f"Erreur lors de la requête : {e}")</p>
</body>
</html>
