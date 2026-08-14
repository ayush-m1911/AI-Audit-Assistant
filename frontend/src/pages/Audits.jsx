import React from 'react';
import { ShieldCheck, Plus } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';

export default function Audits() {
  const headerAction = (
    <button className="btn btn-primary" disabled>
      <Plus size={16} />
      <span>New Audit Request</span>
    </button>
  );

  return (
    <PageContainer 
      title="Compliance Audits" 
      subtitle="Analyze policies against regulatory frameworks with AI Compliance Agents."
      action={headerAction}
    >
      <div className="card">
        <div className="card-body">
          <div className="empty-state">
            <ShieldCheck className="empty-state-icon" style={{ color: 'var(--accent-gold)' }} />
            <h3 className="empty-state-title">Audit Orchestration Pipeline</h3>
            <p className="empty-state-desc" style={{ marginBottom: '24px' }}>
              The interactive query form and LangGraph compliance agent execution pipeline will be activated in Frontend Phase 2.
            </p>
            <div className="api-status" style={{ display: 'inline-flex', alignSelf: 'center' }}>
              <span>Phase 2 Activation Pending</span>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
