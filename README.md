# RAG NotebookLM-like (Gemini) — Backend + UI mínima

Proyecto tipo RAG inspirado en NotebookLM: el usuario sube un documento y el sistema:
- Indexa el contenido en fragmentos (chunks)
- Permite chatear con el documento (RAG)
- Genera un resumen
- Genera un plan de estudio
- Genera preguntas de práctica y corrige respuestas usando evidencia del documento

El enfoque es híbrido:
- Recuperación **lexical** con TF-IDF
- Recuperación **semántica** con embeddings y FAISS
- Respuesta generada con **Gemini** usando el contexto recuperado (con citas por chunk)

---

## Estructura del repositorio

```text
rag-notebooklm-like/
  backend/
    app/
      main.py
      core/
        config.py
      api/
        routes/
          documents.py
          chat.py
          outputs.py
      schemas/
        common.py
      services/
        ingest/
          loaders.py
          chunker.py
        index/
          lexical.py
          vectorstore.py
        llm/
          gemini_client.py
        rag/
          pipeline.py
      storage/
        uploads/
        docs/
        indexes/
    requirements.txt
    requirements-dev.txt
    .env.example
  tests/
    conftest.py
    unit/
      test_chunker.py
      test_lexical.py
      test_vectorstore.py
      test_rag_prompt.py
      test_loaders_docx.py
      test_loaders_txt_md.py
    integration/
      test_chat_endpoint.py
      test_documents_upload.py
      test_outputs_endpoints.py
      test_practice_endpoints.py
  web_min/
    index.html
    app.js
  README.md

  




%Definimos un nuevo tipo de medida para las columnas de nuestras tablas y para poder alinear de mejor manera el texto
\newlength\mylength
\newcolumntype{C}[1]{>{\centering\arraybackslash}m{#1}}

\setlength\mylength{\dimexpr\textwidth-5\arrayrulewidth-8\tabcolsep}

% Utiliza longtable para tablas que alcanzan una o más páginas.
% Las letras c,p y m permiten alinear
%En este caso utlizamos la letra C mayúscula porque definimos anteriormente una nueva alineación.
\begin{longtable}
{|C{0.4\mylength}|C{0.3\mylength}|C{0.3\mylength}|} 
\caption{Ejemplo tabla y alineación de texto.}
\label{testtable}\\
\hline
\textbf{Texto Centrado} &\textbf{Texto Centrado} &\textbf{Texto Centrado} \\\hline

\centering\arraybackslash Los comandos en esta celda también permiten centrar el texto. 
& \justify  Este texto aparece justificado.
& Este texto aparece centrado.\\\hline

\multirow{3}{*}{Texto centrado para 3 filas}      &	1 & 0,00\\
                                                  &	2 &	0,00\\
                                                  &	3 &	0,00\\\hline
\multicolumn{3}{|c|}{Texto centrado para 3 columnas} \\\hline

Ejemplo de nota para una tabla \footnotemark & Ejemplo Imagen \includegraphics[width=0.1\textwidth]{Images/firefox.png} & 
PRUEBA
\\\hline
\end{longtable}



Un ejemplo de una figura se presenta en Figura 3.1


 % \clearpage
 
\begin{figure}[ht!]
\centering
\includegraphics[width=0.7\textwidth]{Images/1_files.PNG}
\caption{Ejemplo imagen} 
\label{fig:files}
\end{figure}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   SECCIÓN 3.2
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section[Conclusiones]{Conclusiones}
Presenta lo novedoso del trabajo de integración curricular, así como evaluación del cumplimiento o no de lo propuesto en los objetivos. En el caso en que no se cumpla uno o varios objetivos, y no se logren los resultados esperados, se propone una posible respuesta que explique por qué sucedió esto o las falencias de la planteado. 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   SECCIÓN 3.3
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\section[Recomendaciones]{Recomendaciones}
Indicar las recomendaciones formuladas a partir del desarrollo de este trabajo de integración curricular.