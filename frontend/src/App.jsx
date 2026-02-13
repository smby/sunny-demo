import { useEffect, useMemo, useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE || "http://localhost:8000").replace(/\/$/, "");

const DEFAULTS = {
  EN: {
    positioning:
      "Mid-to-high-end furniture and lighting for residential, staging, and boutique hospitality projects.",
    tone: "confident, practical, consultative",
  },
  CN: {
    positioning: "面向住宅、软装与精品酒店场景的中高端家具与灯具供应方案。",
    tone: "专业、务实、可信",
  },
};

const I18N = {
  EN: {
    language: "Language",
    appTitle: "Sunny Lead Intelligence Copilot",
    subtitle:
      "Demonstrate how AI can transform raw B2B prospect lists into ranked targets, clear reasoning, and outreach-ready drafts.",
    api: "API",
    connected: "Connected",
    unavailable: "Unavailable",
    aiMode: "AI Mode",
    backendReady: "Backend Ready",
    templateOnly: "Template Only",
    runDemo: "Run Demo",
    leadCsv: "Lead CSV",
    loadSample: "Load Sample Data",
    downloadTemplate: "Download Lead Template",
    noFile: "No file selected",
    targetStates: "Target States",
    brandName: "Brand Name",
    positioning: "Positioning Context",
    tone: "Outreach Tone",
    useAi: "Use AI-generated outreach (requires backend API key)",
    aiLeadLimit: "AI Lead Limit",
    processing: "Processing...",
    runLeadIntel: "Run Lead Intelligence",
    capabilityStory: "Capability Story",
    capabilityItems: [
      "Ingest mixed-quality lead data from manual research or purchased lists.",
      "Score each account by vertical fit, buying intent, and digital readiness.",
      "Produce explainable ranking to prioritize sales execution.",
      "Generate outreach drafts for top accounts in a consistent tone.",
      "Export outputs for CRM import and rep execution.",
    ],
    potentialCapabilities: "Potential Capabilities (Not in Demo Yet)",
    potentialItems: [
      "Automated daily/weekly performance reports by platform.",
      "Storefront operations support (merchandising and product display updates).",
      "Social account operations (short video and post publishing).",
      "After-sales and logistics tracking across shopping platforms.",
      "Supply-chain workflows (price checks, purchasing, and data entry).",
    ],
    trustSignalTitle: "Trust signal:",
    trustSignalText:
      "This demo makes decisions transparent. Every lead has a reason, score, tier, and ready-to-use outreach draft.",
    totalLeads: "Total Leads",
    averageScore: "Average Score",
    tierDistribution: "Tier Distribution",
    topStates: "Top States",
    rankedLeads: "Ranked Leads",
    downloadCsv: "Download CSV",
    downloadReport: "Download Report",
    company: "Company",
    state: "State",
    score: "Score",
    tier: "Tier",
    reason: "Reason",
    leadDetail: "Lead Detail",
    downloadDraft: "Download Draft",
    noWebsite: "No website",
    subject: "Subject",
    outreachDraft: "Outreach Draft",
    runToInspect: "Run the demo to inspect lead details.",
    loadSampleError: "Could not load sample file",
    sampleDataError: "Failed to load sample data.",
    fileRequired: "Please upload a CSV file (or load the sample file).",
    processFailed: "Failed to process leads.",
    unexpectedError: "Unexpected error while processing leads.",
    notAvailable: "N/A",
    rankedCsvFile: "ranked_leads.csv",
    leadTemplateFile: "lead_template.csv",
    reportFile: "top_leads_outreach.md",
    draftPrefix: "outreach",
    copy: "Copy",
    copied: "Copied",
    refineFeedback: "Refine Feedback",
    refineHint: "Example: make it shorter, friendlier, and add a stronger CTA.",
    refineButton: "AI Refine",
    refining: "Refining...",
    refineRequired: "Please enter feedback before refining.",
    refineFailed: "Failed to refine outreach.",
    aiUnavailable: "AI is not available on backend. Check OPENAI_API_KEY and restart backend.",
    breakdownLabels: {
      industry_fit: "industry fit",
      product_match: "product match",
      digital_signal: "digital signal",
      scale_signal: "scale signal",
      intent_signal: "intent signal",
      penalties: "penalties",
    },
  },
  CN: {
    language: "语言",
    appTitle: "Sunny 线索智能助手",
    subtitle: "展示 AI 如何把原始 B2B 线索清单转化为可解释的优先级排序和可直接发送的外联草稿。",
    api: "接口状态",
    connected: "已连接",
    unavailable: "不可用",
    aiMode: "AI 模式",
    backendReady: "后端可用",
    templateOnly: "模板模式",
    runDemo: "运行演示",
    leadCsv: "线索 CSV",
    loadSample: "加载示例数据",
    downloadTemplate: "下载线索模板",
    noFile: "未选择文件",
    targetStates: "目标州",
    brandName: "品牌名称",
    positioning: "业务定位说明",
    tone: "外联语气",
    useAi: "启用 AI 生成外联文案（需要后端 API Key）",
    aiLeadLimit: "AI 生成上限",
    processing: "处理中...",
    runLeadIntel: "运行线索智能分析",
    capabilityStory: "能力展示",
    capabilityItems: [
      "接收来源混杂、质量不一的线索数据。",
      "按行业匹配、采购意向和数字化信号进行评分。",
      "输出可解释的优先级排序，辅助销售执行。",
      "为高优先级客户生成一致风格的外联草稿。",
      "导出结果，便于 CRM 导入与团队执行。",
    ],
    potentialCapabilities: "潜在能力（不在当前 Demo 中）",
    potentialItems: [
      "各平台数据统计报表（日报/周报自动生成）。",
      "购物平台店铺运营支持（商品陈列与店铺装修更新）。",
      "社媒账号运营（短视频与图文内容发布）。",
      "多平台售后与物流跟踪。",
      "供应链流程支持（核价、采购、信息录入）。",
    ],
    trustSignalTitle: "信任信号：",
    trustSignalText: "这个 Demo 的每条线索都可解释：有原因、有分数、有等级、还有可直接使用的外联文案。",
    totalLeads: "线索总数",
    averageScore: "平均得分",
    tierDistribution: "等级分布",
    topStates: "重点州",
    rankedLeads: "线索排序结果",
    downloadCsv: "下载 CSV",
    downloadReport: "下载报告",
    company: "公司",
    state: "州",
    score: "得分",
    tier: "等级",
    reason: "原因",
    leadDetail: "线索详情",
    downloadDraft: "下载草稿",
    noWebsite: "无网站",
    subject: "标题",
    outreachDraft: "外联草稿",
    runToInspect: "先运行演示以查看线索详情。",
    loadSampleError: "无法加载示例文件",
    sampleDataError: "加载示例数据失败。",
    fileRequired: "请先上传 CSV 文件（或加载示例数据）。",
    processFailed: "线索处理失败。",
    unexpectedError: "处理过程中出现异常。",
    notAvailable: "暂无",
    rankedCsvFile: "线索排序结果.csv",
    leadTemplateFile: "线索模板.csv",
    reportFile: "高优先级线索外联草稿.md",
    draftPrefix: "外联草稿",
    copy: "复制",
    copied: "已复制",
    refineFeedback: "优化反馈",
    refineHint: "示例：更简短、更自然，并加强明确行动号召。",
    refineButton: "AI 优化文案",
    refining: "优化中...",
    refineRequired: "请先填写优化反馈。",
    refineFailed: "外联文案优化失败。",
    aiUnavailable: "后端 AI 不可用，请检查 OPENAI_API_KEY 并重启后端。",
    breakdownLabels: {
      industry_fit: "行业匹配",
      product_match: "品类匹配",
      digital_signal: "数字信号",
      scale_signal: "规模信号",
      intent_signal: "意向信号",
      penalties: "负向项",
    },
  },
};

function toCsvCell(value) {
  const text = String(value ?? "");
  if (text.includes(",") || text.includes("\n") || text.includes("\"")) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function leadRowsToCsv(leads) {
  if (!leads?.length) return "";
  const headers = [
    "company_name",
    "city",
    "state",
    "website",
    "source",
    "score",
    "tier",
    "reason",
    "outreach_subject",
    "outreach_message",
  ];

  const lines = [headers.join(",")];
  for (const lead of leads) {
    const row = headers.map((key) => toCsvCell(lead[key]));
    lines.push(row.join(","));
  }
  return lines.join("\n");
}

function downloadText(filename, content, mime = "text/plain") {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function App() {
  const [language, setLanguage] = useState("CN");
  const [file, setFile] = useState(null);
  const [targetStates, setTargetStates] = useState("AZ,CA,TX,FL,NY");
  const [brandName, setBrandName] = useState("Sunny Home");
  const [positioning, setPositioning] = useState(DEFAULTS.CN.positioning);
  const [tone, setTone] = useState(DEFAULTS.CN.tone);
  const [useAI, setUseAI] = useState(false);
  const [aiLimit, setAiLimit] = useState(8);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [health, setHealth] = useState(null);
  const [refineFeedback, setRefineFeedback] = useState("");
  const [refining, setRefining] = useState(false);
  const [copiedField, setCopiedField] = useState("");

  const t = I18N[language];
  const selectedLead = result?.leads?.[selectedIndex] || null;

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/health`);
        if (!res.ok) return;
        const data = await res.json();
        setHealth(data);
      } catch {
        setHealth(null);
      }
    };
    checkHealth();
  }, []);

  useEffect(() => {
    const other = language === "CN" ? "EN" : "CN";
    setPositioning((prev) => (prev === DEFAULTS[other].positioning ? DEFAULTS[language].positioning : prev));
    setTone((prev) => (prev === DEFAULTS[other].tone ? DEFAULTS[language].tone : prev));
  }, [language]);

  const topStates = useMemo(() => {
    return (result?.summary?.top_states || []).map((item) => {
      const [state, count] = Object.entries(item)[0] || [t.notAvailable, 0];
      return { state, count };
    });
  }, [result, t.notAvailable]);

  const loadSampleFile = async () => {
    try {
      const response = await fetch("/sample_leads.csv");
      if (!response.ok) throw new Error(t.loadSampleError);
      const blob = await response.blob();
      const sample = new File([blob], "sample_leads.csv", { type: "text/csv" });
      setFile(sample);
      setError("");
    } catch (err) {
      setError(err.message || t.sampleDataError);
    }
  };

  const downloadLeadTemplate = async () => {
    try {
      const response = await fetch("/lead_template.csv");
      if (!response.ok) throw new Error(t.loadSampleError);
      const text = await response.text();
      downloadText(t.leadTemplateFile, text, "text/csv;charset=utf-8");
      setError("");
    } catch (err) {
      setError(err.message || t.sampleDataError);
    }
  };

  const processLeads = async (event) => {
    event.preventDefault();
    setError("");

    if (!file) {
      setError(t.fileRequired);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_states", targetStates);
    formData.append("brand_name", brandName);
    formData.append("positioning", positioning);
    formData.append("tone", tone);
    formData.append("language", language);
    formData.append("use_ai", String(useAI));
    formData.append("ai_limit", String(aiLimit));

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/process`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || t.processFailed);
      }

      const data = await response.json();
      setResult(data);
      setSelectedIndex(0);
    } catch (err) {
      setError(err.message || t.unexpectedError);
    } finally {
      setLoading(false);
    }
  };

  const downloadRankedCsv = () => {
    if (!result?.leads?.length) return;
    const csv = leadRowsToCsv(result.leads);
    downloadText(t.rankedCsvFile, csv, "text/csv;charset=utf-8");
  };

  const downloadReport = () => {
    if (!result?.top_leads_markdown) return;
    downloadText(t.reportFile, result.top_leads_markdown, "text/markdown;charset=utf-8");
  };

  const downloadLeadDraft = () => {
    if (!selectedLead) return;
    const content = `${selectedLead.outreach_subject}\n\n${selectedLead.outreach_message}`;
    const safeName = selectedLead.company_name.replace(/\s+/g, "_");
    downloadText(`${t.draftPrefix}_${safeName}.txt`, content);
  };

  const copyText = async (field, text) => {
    try {
      await navigator.clipboard.writeText(text || "");
      setCopiedField(field);
      setTimeout(() => setCopiedField(""), 1200);
    } catch {
      setError(t.unexpectedError);
    }
  };

  const refineSelectedOutreach = async () => {
    if (!selectedLead) return;
    if (!refineFeedback.trim()) {
      setError(t.refineRequired);
      return;
    }
    if (!health?.ai_enabled) {
      setError(t.aiUnavailable);
      return;
    }

    setRefining(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/refine-outreach`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language,
          tone,
          brand_name: brandName,
          positioning,
          company_name: selectedLead.company_name,
          city: selectedLead.city || "",
          state: selectedLead.state || "",
          services: selectedLead.services || "",
          description: selectedLead.description || "",
          current_subject: selectedLead.outreach_subject,
          current_message: selectedLead.outreach_message,
          feedback: refineFeedback,
        }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || t.refineFailed);
      }

      const data = await response.json();
      setResult((prev) => {
        if (!prev) return prev;
        const nextLeads = [...prev.leads];
        const current = nextLeads[selectedIndex];
        nextLeads[selectedIndex] = {
          ...current,
          outreach_subject: data.subject,
          outreach_message: data.message,
        };
        return { ...prev, leads: nextLeads };
      });
    } catch (err) {
      setError(err.message || t.refineFailed);
    } finally {
      setRefining(false);
    }
  };

  return (
    <div className="page-shell">
      <div className="background-shape bg-1" />
      <div className="background-shape bg-2" />

      <header className="hero panel">
        <div>
          <p className="eyebrow">Cognitive Labs</p>
          <h1>{t.appTitle}</h1>
          <p className="subtitle">{t.subtitle}</p>
        </div>
        <div className="status-stack-wrap">
          <div className="language-toggle" role="group" aria-label={t.language}>
            <button type="button" className={`lang-btn ${language === "CN" ? "active" : ""}`} onClick={() => setLanguage("CN")}>
              CN
            </button>
            <button type="button" className={`lang-btn ${language === "EN" ? "active" : ""}`} onClick={() => setLanguage("EN")}>
              EN
            </button>
          </div>
          <div className="status-stack">
            <div className="status-card">
              <span>{t.api}</span>
              <strong>{health ? t.connected : t.unavailable}</strong>
            </div>
            <div className="status-card">
              <span>{t.aiMode}</span>
              <strong>{health?.ai_enabled ? t.backendReady : t.templateOnly}</strong>
            </div>
          </div>
        </div>
      </header>

      <section className="control-grid">
        <form className="panel form-panel" onSubmit={processLeads}>
          <h2>{t.runDemo}</h2>

          <label className="field">
            <span>{t.leadCsv}</span>
            <input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          </label>

          <div className="row-actions">
            <div className="button-group">
              <button type="button" className="ghost" onClick={loadSampleFile}>
                {t.loadSample}
              </button>
              <button type="button" className="ghost" onClick={downloadLeadTemplate}>
                {t.downloadTemplate}
              </button>
            </div>
            <span className="small-muted">{file ? file.name : t.noFile}</span>
          </div>

          <label className="field">
            <span>{t.targetStates}</span>
            <input value={targetStates} onChange={(e) => setTargetStates(e.target.value)} />
          </label>

          <label className="field">
            <span>{t.brandName}</span>
            <input value={brandName} onChange={(e) => setBrandName(e.target.value)} />
          </label>

          <label className="field">
            <span>{t.positioning}</span>
            <textarea rows={3} value={positioning} onChange={(e) => setPositioning(e.target.value)} />
          </label>

          <label className="field">
            <span>{t.tone}</span>
            <input value={tone} onChange={(e) => setTone(e.target.value)} />
          </label>

          <div className="toggle-row">
            <label className="switch">
              <input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} />
              <span>{t.useAi}</span>
            </label>
            <label className="field mini">
              <span>{t.aiLeadLimit}</span>
              <input type="number" min={1} max={20} value={aiLimit} onChange={(e) => setAiLimit(Number(e.target.value) || 8)} />
            </label>
          </div>

          <button type="submit" className="primary" disabled={loading}>
            {loading ? t.processing : t.runLeadIntel}
          </button>
        </form>

        <aside className="panel guidance-panel">
          <h2>{t.capabilityStory}</h2>
          <ol>
            {t.capabilityItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
          <div className="note">
            <strong>{t.trustSignalTitle}</strong> {t.trustSignalText}
          </div>
          <div className="section-divider" />
          <h3>{t.potentialCapabilities}</h3>
          <ol>
            {t.potentialItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
          <div className="section-divider" />
        </aside>
      </section>

      {error && <div className="panel error-box">{error}</div>}

      {result && (
        <>
          <section className="metrics-grid">
            <article className="metric panel">
              <span>{t.totalLeads}</span>
              <strong>{result.summary.total_leads}</strong>
            </article>
            <article className="metric panel">
              <span>{t.averageScore}</span>
              <strong>{result.summary.average_score}</strong>
            </article>
            <article className="metric panel">
              <span>{t.tierDistribution}</span>
              <strong>
                A {result.summary.tier_a} | B {result.summary.tier_b} | C {result.summary.tier_c}
              </strong>
            </article>
            <article className="metric panel">
              <span>{t.topStates}</span>
              <strong>{topStates.map((item) => `${item.state} (${item.count})`).join("  •  ") || t.notAvailable}</strong>
            </article>
          </section>

          <section className="result-grid">
            <div className="panel table-panel">
              <div className="panel-header">
                <h2>{t.rankedLeads}</h2>
                <div className="button-group">
                  <button type="button" className="ghost" onClick={downloadRankedCsv}>
                    {t.downloadCsv}
                  </button>
                  <button type="button" className="ghost" onClick={downloadReport}>
                    {t.downloadReport}
                  </button>
                </div>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>{t.company}</th>
                      <th>{t.state}</th>
                      <th>{t.score}</th>
                      <th>{t.tier}</th>
                      <th>{t.reason}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.leads.map((lead, index) => (
                      <tr
                        key={`${lead.company_name}-${index}`}
                        onClick={() => setSelectedIndex(index)}
                        className={index === selectedIndex ? "active" : ""}
                      >
                        <td>{lead.company_name}</td>
                        <td>{lead.state || "-"}</td>
                        <td>{lead.score}</td>
                        <td>
                          <span className={`tier-chip tier-${lead.tier.toLowerCase()}`}>{lead.tier}</span>
                        </td>
                        <td>{lead.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="panel detail-panel">
              <div className="panel-header">
                <h2>{t.leadDetail}</h2>
                <div className="button-group">
                  <button type="button" className="ghost" onClick={downloadLeadDraft} disabled={!selectedLead}>
                    {t.downloadDraft}
                  </button>
                </div>
              </div>

              {selectedLead ? (
                <>
                  <h3>{selectedLead.company_name}</h3>
                  <p className="detail-meta">
                    {selectedLead.city}, {selectedLead.state} · {selectedLead.website || t.noWebsite}
                  </p>
                  <p className="reason">{selectedLead.reason}</p>

                  <div className="breakdown-grid">
                    {Object.entries(selectedLead.breakdown).map(([key, value]) => {
                      if (key === "total") return null;
                      return (
                        <div key={key} className="break-item">
                          <span>{t.breakdownLabels[key] || key.replace(/_/g, " ")}</span>
                          <strong>{value}</strong>
                        </div>
                      );
                    })}
                  </div>

                  <label className="field">
                    <span>{t.subject}</span>
                    <div className="inline-field-actions">
                      <input value={selectedLead.outreach_subject} readOnly />
                      <button
                        type="button"
                        className="ghost"
                        onClick={() => copyText("subject", selectedLead.outreach_subject)}
                      >
                        {copiedField === "subject" ? t.copied : t.copy}
                      </button>
                    </div>
                  </label>

                  <label className="field">
                    <span>{t.outreachDraft}</span>
                    <textarea rows={9} value={selectedLead.outreach_message} readOnly />
                  </label>
                  <div className="button-group">
                    <button
                      type="button"
                      className="ghost"
                      onClick={() => copyText("message", selectedLead.outreach_message)}
                    >
                      {copiedField === "message" ? t.copied : t.copy}
                    </button>
                  </div>

                  <label className="field">
                    <span>{t.refineFeedback}</span>
                    <textarea
                      rows={3}
                      placeholder={t.refineHint}
                      value={refineFeedback}
                      onChange={(e) => setRefineFeedback(e.target.value)}
                    />
                  </label>
                  <div className="refine-action">
                    <button type="button" className="primary" onClick={refineSelectedOutreach} disabled={refining}>
                      {refining ? t.refining : t.refineButton}
                    </button>
                  </div>
                </>
              ) : (
                <p className="small-muted">{t.runToInspect}</p>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default App;
