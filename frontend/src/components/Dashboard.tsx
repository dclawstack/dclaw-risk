"use client";

import { useState } from "react";
import { ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface RiskAssessment {
  id: string;
  name: string;
  category: string;
  severity: number;
  probability: number;
  mitigation_status: string;
  owner: string;
  created_at: string
}

export default function Dashboard() {
  const [riskName, setRiskName] = useState("");
const [category, setCategory] = useState("Operational");
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessment | null>(null);
  const [extraData, setExtraData] = useState<any>(null);
const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (!riskName || !category) return;
    setLoading(true);
    try {
      const res = await fetch("/assessments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        riskName: riskName,
        category: category,
        }),
      });
      const data = await res.json();
      setRiskAssessment(data);
      const extraRes = await fetch(`/assessments/${assessment_id}/mitigations`);
      const extraData = await extraRes.json();
      setExtraData(extraData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <ShieldAlert className="w-8 h-8" style={{ color: "#DC2626" }} />
        <div>
          <h1 className="text-2xl font-bold">DClaw Risk</h1>
          <p className="text-sm text-slate-500">Enterprise risk management</p>
        </div>
        <Badge className="ml-auto" style={{ backgroundColor: "#DC2626" }}>Governance</Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Assess Risk</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Risk name</label>
              <Input value={riskName} onChange={(e) => setRiskName(e.target.value)} placeholder="e.g. Data breach liability" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="flex h-9 w-full rounded-md border border-slate-200 bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-brand">
                <option value="Operational">Operational</option><option value="Financial">Financial</option><option value="Legal">Legal</option><option value="Reputational">Reputational</option>
              </select>
            </div>
          </div>
          <Button onClick={handleSubmit} disabled={loading || !riskName || !category}>
            {loading ? "Processing..." : "Assess Risk"}
          </Button>
        </CardContent>
      </Card>

      {riskAssessment && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          <Card>
            <CardHeader>
              <CardTitle>Assessment Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p><strong>ID:</strong> {assessment.id}</p>
              <p><strong>Name:</strong> {assessment.name}</p>
              <p><strong>Category:</strong> {assessment.category}</p>
              <p><strong>Severity:</strong> {assessment.severity + '/5'}</p>
              <p><strong>Probability:</strong> {assessment.probability + '/5'}</p>
              <p><strong>Mitigation Status:</strong> {assessment.mitigation_status}</p>
              <p><strong>Owner:</strong> {assessment.owner}</p>
              <p><strong>Created:</strong> {new Date(assessment.created_at).toLocaleString()}</p>
            </CardContent>
          </Card>
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Mitigation Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {extraData?.map((rec: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                    <span className="text-sm">{rec.action}</span>
                    <Badge variant="secondary">{rec.owner}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
