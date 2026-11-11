import pandas as pd, re, glob, os
from pathlib import Path
# Run from the Overleaf project root or from prisma/scripts.
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'prisma' / 'data' / 'screening_batches'
OUT = ROOT / 'prisma' / 'data' / 'screening_results_recomputed'
OUT.mkdir(exist_ok=True)

def norm(s):
    if pd.isna(s): return ''
    return str(s).lower().replace('—','-').replace('–','-').replace('\u00a0',' ')

def has_any(text, phrases):
    return any(p in text for p in phrases)

def rx(text, pattern):
    return re.search(pattern, text, flags=re.I|re.S) is not None

llm_terms = ['large language model','large language models',' llm',' llms','language model','language models','chatgpt','gpt-','gpt ','generative ai','genai','generative artificial intelligence','foundation model','foundation models','conversational ai','chatbot','chatbots','ai assistant','ai assistants','copilot','copilots','agentic ai']
agent_terms = ['llm agent','llm agents','ai agent','ai agents','autonomous agent','autonomous agents','agentic','tool-using','tool using','tool-use','tool use','function calling','external tools','planner','multi-agent','multi agent','mcp','agent-to-agent']
llm_attack_terms = ['prompt injection','indirect prompt injection','jailbreak','jailbreaking','adversarial prompt','prompt attack','malicious instruction','instruction attack','red team','red-teaming','red teaming','tool poisoning','memory poisoning','agent hijack']
rag_attack_terms = ['poisonedrag','poisoned rag','knowledge corruption','knowledge poisoning','corpus poisoning','retrieval poisoning','rag poisoning','retrieval-augmented generation attack','retrieval augmented generation attack','retrieval manipulation','adversarial retrieval']
strong_security_terms = ['security','cybersecurity','cyber security','attack','threat','vulnerability','malicious','exploit','abuse','defense','defence','mitigation','poisoning','jailbreak','prompt injection']
weak_risk_terms = ['safety','robustness','reliability','privacy','risk','trustworthy']
provenance_strong_terms = ['provenance','lineage','traceability','auditability','audit trail','attestation','tamper-evident','transparency log','source attribution','citation provenance','source credibility','source reliability']
epistemic_strong_terms = ['epistemic security','epistemic integrity','epistemic trust','epistemic agency','epistemic vigilance','epistemic injustice','epistemic risk','cognitive security','knowledge integrity','information integrity']
factual_strong_terms = ['hallucination','hallucinations','factuality','fact-checking','fact checking','claim verification','source verification','citation grounding','truthfulness','misinformation','disinformation','fake news','information disorder']
factual_background_terms = ['rumor','rumour','credibility assessment','information credibility']
human_trust_terms = ['automation bias','over-reliance','overreliance','trust calibration','calibrated trust','appropriate reliance','reliance on ai','human-ai trust','human ai trust','operator trust','user trust','trustworthy ai','cognitive bias']
hai_terms = ['human-ai','human ai','human-ai interaction','human-centered ai','human centred ai','human-centered','human centered','human-machine','human machine','human-automation','human automation','ai-assisted decision','ai assisted decision','ai-supported decision','algorithmic decision','decision support','decision-making','decision making','explainable ai','xai','explainability','transparency','interpretability','accountability']
cyber_decision_terms = ['cybersecurity analyst','security analyst','soc analyst','soc ','security operations','incident response','threat intelligence','threat hunting','cyber defense','cyber defence']
gov_terms = ['zero trust','zero-trust','ai governance','responsible ai','nist ai rmf','assurance','compliance','policy']
gov_broad_terms = ['governance','risk management']
survey_terms = ['survey','systematic review','systematic literature review','literature review','mapping study','review','sok','taxonomy','benchmark','benchmarking','dataset']

out_scope_cv = ['image classification','object detection','segmentation','medical image','computed tomography','magnetic resonance','x-ray','x ray','histopathology','microscopic images','leukaemia','leukemia','cancer diagnosis','skin lesion','diabetic retinopathy','traffic sign detection','facial expression','face recognition','activity recognition','machine vision']
hardware_terms = ['side-channel','side channel','power analysis','fault injection','accelerator','fpga','hardware trojan','neural network accelerator','chip','microcontroller']
nontech_doc_types = ['editorial','note','letter','meeting abstract','erratum','retracted']

def has_rag(text):
    if 'retrieval-augmented' in text or 'retrieval augmented' in text or 'retrieval augmentation' in text:
        return True
    if rx(text, r'\brag\b') and not rx(text, r'\brag-?1\b'):
        return has_any(text, ['retrieval','generation','generative','llm','large language model','chatbot','knowledge base','vector database','query','document'])
    return False

def has_ai_indicator(text):
    return has_any(text, ['artificial intelligence','machine learning','deep learning',' ai ',' ai-','-ai',' ai.',' ai,','algorithmic','automated decision'])

def is_prompt_injection_security_context(text):
    if 'prompt injection' not in text:
        return False
    # If clearly used as a benign prompt-engineering phrase and no malicious/safeguard/security context, treat as background.
    if 'document-based prompt injection' in text and not has_any(text, ['attack','attacks','malicious','adversarial','security','safeguard','misuse','defense','defence','threat']):
        return False
    return True

def classify_row(row):
    title = norm(row.get('title',''))
    abstract = norm(row.get('abstract',''))
    venue = norm(row.get('venue',''))
    doctype = norm(row.get('document_type',''))
    text = re.sub(r'\s+', ' ', ' '.join([title, abstract, venue, doctype]))
    abstract_empty = (not abstract.strip()) or abstract.strip() == 'nan'

    h_llm = has_any(text, llm_terms)
    h_rag = has_rag(text)
    h_agent = has_any(text, agent_terms)
    h_strong_sec = has_any(text, strong_security_terms)
    h_weak_risk = has_any(text, weak_risk_terms)
    h_prov = has_any(text, provenance_strong_terms)
    h_epi = has_any(text, epistemic_strong_terms)
    h_fact = has_any(text, factual_strong_terms)
    h_fact_bg = h_fact or has_any(text, factual_background_terms)
    h_htrust = has_any(text, human_trust_terms) or (('trust' in text or 'distrust' in text) and has_any(text, ['human-ai','human ai','automation','ai-assisted','algorithmic decision','decision-making','decision making']))
    h_hai = has_any(text, hai_terms)
    h_cyber = has_any(text, cyber_decision_terms)
    h_gov = has_any(text, gov_terms) or (has_any(text, gov_broad_terms) and (h_llm or h_agent or h_rag or has_ai_indicator(text)))
    h_survey = has_any(text, survey_terms)
    h_ai = h_llm or h_agent or h_rag or has_ai_indicator(text)

    if any(dt == doctype.strip() or dt in doctype for dt in nontech_doc_types):
        if not (has_any(text, llm_attack_terms + rag_attack_terms) or (h_llm and h_strong_sec) or h_epi):
            return 'exclude','no_technical_content','document type is editorial/commentary or otherwise lacks screenable technical contribution'

    # CORE direct attack/security/epistemic-integrity evidence.
    if has_any(text, rag_attack_terms):
        return 'include_core','', 'RAG/corpus knowledge-corruption or adversarial retrieval attack directly in scope'
    if is_prompt_injection_security_context(text):
        return 'include_core','', 'prompt-injection threat to LLM/RAG/agent workflows'
    if h_llm and has_any(text, ['jailbreak','jailbreaking','adversarial prompt','prompt attack','malicious instruction','red team','red-teaming','red teaming','tool poisoning','memory poisoning']):
        return 'include_core','', 'LLM adversarial prompting, jailbreak, or tool/memory attack directly in scope'
    if h_epi:
        return 'include_core','', 'directly addresses epistemic integrity, epistemic trust, or cognitive security'
    if (h_llm or h_agent or h_rag) and h_strong_sec and has_any(text, ['agent security','llm security','large language model security','secure llm','security of llm','security for llm','threat model','attack surface','vulnerability','security analysis','security challenges','privacy and security']):
        if has_any(title, ['security','privacy','attack','threat','vulnerability','secure','risk','safety','jailbreak','prompt injection','poisoning','red team','malicious','defense','defence']) or has_any(text, ['threat model','attack surface','privacy and security challenges','security analysis of']):
            return 'include_core','', 'LLM/RAG/agent security or threat-model contribution directly in scope'
        return 'include_background','', 'LLM/RAG/agent security-relevant background without a primary attack or defense focus'
    if h_rag and h_strong_sec and has_any(text, ['attack','threat','poisoning','adversarial','vulnerability','security','privacy and security','defense','defence','mitigation']):
        if has_any(text, ['attack','attacks','threat','poisoning','adversarial retrieval','vulnerability','malicious','prompt injection']) or has_any(title, ['security','secure','privacy','attack','poisoning','vulnerability','adversarial','threat','defense','defence','mitigation']):
            return 'include_core','', 'RAG security, attack, or defense evidence directly supports the corpus'
        return 'include_background','', 'RAG robustness or reliability work relevant as background for retrieval-mediated risk'
    if (h_llm or h_rag or h_agent) and h_prov and (h_strong_sec or h_fact or h_gov):
        if has_any(text, ['provenance','lineage','attestation','auditability','audit trail','traceability','transparency log','citation provenance']) or (h_fact and has_any(text, ['source attribution','source credibility','source reliability','citation grounding'])):
            return 'include_core','', 'provenance, lineage, or source-control mechanism for AI-mediated claims'
        return 'include_background','', 'source-control or credibility signal relevant as background for AI-mediated claims'
    if (h_llm or h_rag) and h_fact:
        return 'include_core','', 'LLM/RAG factuality, hallucination, verification, or misinformation-control evidence'
    if h_cyber and (h_llm or h_agent or h_hai) and (h_htrust or h_prov or h_fact or h_strong_sec or h_weak_risk):
        return 'include_core','', 'AI-assisted cybersecurity decision support with trust, evidence, or attack relevance'
    if h_survey and (h_llm or h_agent or h_rag) and h_strong_sec:
        if has_any(title, ['security','privacy','attack','threat','vulnerability','jailbreak','prompt injection','poisoning','red team','safety evaluation','risk assessment']):
            return 'include_core','', 'survey/benchmark of LLM, RAG, or agent security directly maps the evidence base'
        return 'include_background','', 'general LLM/RAG/agent survey with security or reliability relevance; useful background rather than core evidence'

    # BACKGROUND adjacent evidence.
    if h_llm and 'prompt injection' in text:
        return 'include_background','', 'LLM prompt-engineering/injection context is adjacent but not clearly adversarial from abstract'
    if h_htrust and h_ai:
        return 'include_background','', 'human-AI trust, reliance, calibration, or automation-bias evidence useful for the threat model'
    if h_hai and h_ai and has_any(text, ['high-stakes','clinical decision support','medical decision','healthcare decision','legal decision','security operations','cybersecurity','incident response','operator','analyst','explainability','transparency','interpretability','accountability','trust','human factors']):
        return 'include_background','', 'human-AI decision-support or explainability evidence useful as background'
    if h_fact_bg and not (h_llm or h_rag or h_agent):
        return 'include_background','', 'information-integrity, fact-checking, or misinformation literature useful as background'
    if h_prov and not has_any(text, ['seismic','nuclear','geological','genome','biology','taxonomic','hydrological']) and (h_ai or h_gov or h_hai or h_strong_sec or h_survey):
        return 'include_background','', 'provenance, auditability, or source-credibility literature supports the control architecture'
    if h_gov and h_ai:
        return 'include_background','', 'AI governance, zero-trust, or assurance framing relevant to CZTA controls'
    if h_survey and (h_llm or h_rag) and not h_strong_sec:
        return 'include_background','', 'general LLM/RAG survey or benchmark useful as background context'
    if h_rag and (h_weak_risk or has_any(text, ['evaluation','metrics','challenge','challenges','benchmark','grounding','citation','relevance','quality','reliability'])):
        return 'include_background','', 'RAG methods or evaluation background relevant to retrieval-mediated epistemic risk'
    if h_llm and has_any(text, ['explainability','transparency','interpretability','trustworthy','responsible ai','accountability','ethics']) and not has_any(text, ['poetry','creative writing']):
        return 'include_background','', 'LLM transparency, accountability, or responsible-use background relevant to governance'

    if abstract_empty:
        if has_any(title, ['trust','transparency','provenance','epistemic','rag','llm','large language model','prompt','agent','decision support','misinformation','disinformation','zero trust','human-ai','human ai','ai governance']):
            return 'uncertain','', 'abstract missing or too sparse; title suggests possible relevance but full text is needed'
        return 'exclude','not_ai_security','abstract missing and title/venue do not indicate AI-security relevance'

    # Out-of-scope AI security and generic AI.
    if h_strong_sec or has_any(text, ['adversarial example','backdoor','trojan','membership inference','model extraction','model inversion','federated learning','side-channel','poisoning attack']):
        if has_any(text, hardware_terms):
            return 'exclude','not_within_scope','AI/security paper focused on hardware or side-channel threats outside epistemic/agent scope'
        if has_any(text, out_scope_cv) and not (h_llm or h_rag or h_agent or h_htrust):
            return 'exclude','not_within_scope','computer-vision or domain ML security without LLM, RAG, agent, or human-trust angle'
        if has_any(text, ['adversarial example','backdoor','trojan','membership inference','model extraction','model inversion','federated learning','fault injection']) and not (h_llm or h_rag or h_agent or h_htrust or h_fact or h_prov):
            return 'exclude','not_within_scope','AI-security topic is outside epistemic, RAG, agent, provenance, or human-AI trust scope'
    if h_ai:
        return 'exclude','not_ai_security','AI/LLM application lacks epistemic-security, provenance, misinformation, attack, or human-trust focus'
    return 'exclude','not_ai_security','no AI-security or AI-assisted decision-making security relevance apparent from title/abstract'


def main():
    all_res=[]
    for f in sorted(BASE.glob('batch_*.csv')):
        df=pd.read_csv(f)
        rows=[]
        for _, row in df.iterrows():
            dec, reason, note = classify_row(row)
            if dec != 'exclude': reason=''
            rows.append({'record_id': row['record_id'], 'screening_decision': dec, 'exclusion_reason': reason, 'notes': note})
        out=pd.DataFrame(rows, columns=['record_id','screening_decision','exclusion_reason','notes'])
        out.to_csv(OUT/(f.stem+'_results.csv'), index=False)
        all_res.append(out.assign(batch=f.name))
    res=pd.concat(all_res, ignore_index=True)
    res.to_csv(ROOT/'prisma/data/processed/P3_screening_results_all_batches_recomputed.csv', index=False)
    print(res.screening_decision.value_counts().to_string())
    print('\nExclusion reasons')
    print(res.exclusion_reason.value_counts(dropna=False).to_string())
    print('\nNotes')
    print(res.notes.value_counts().to_string())

if __name__=='__main__':
    main()
