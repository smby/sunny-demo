from __future__ import annotations

from datetime import datetime, timezone


def top_leads_markdown(leads: list[dict], top_n: int = 10, language: str = "EN") -> str:
    cn = language.upper() == "CN"
    top_rows = leads[:top_n]
    lines = [
        "# 高优先级线索 + 外联草稿" if cn else "# Top Leads + Outreach Drafts",
        "",
        (
            f"生成时间: {datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}"
            if cn
            else f"Generated: {datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}"
        ),
        "",
    ]

    for idx, lead in enumerate(top_rows, start=1):
        lines.extend(
            [
                f"## {idx}. {lead['company_name']} ({lead['city']}, {lead['state']})",
                (f"- 评分: **{lead['score']}** (等级 {lead['tier']})" if cn else f"- Score: **{lead['score']}** (Tier {lead['tier']})"),
                (f"- 原因: {lead['reason']}" if cn else f"- Why: {lead['reason']}"),
                (f"- 网站: {lead['website']}" if cn else f"- Website: {lead['website']}"),
                (f"- 标题: {lead['outreach_subject']}" if cn else f"- Subject: {lead['outreach_subject']}"),
                "- 外联草稿:" if cn else "- Outreach Draft:",
                "```text",
                lead["outreach_message"],
                "```",
                "",
            ]
        )

    return "\n".join(lines)
