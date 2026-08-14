import React from 'react';
import { UserCheck } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';

export default function Reviews() {
  return (
    <PageContainer 
      title="Reviews & HITL" 
      subtitle="Audit operations requiring manual validation or additional evidence overrides."
    >
      <div className="card">
        <div className="card-body">
          <div className="empty-state">
            <UserCheck className="empty-state-icon" style={{ color: 'var(--accent-gold)' }} />
            <h3 className="empty-state-title">Human-in-the-Loop Intercepts</h3>
            <p className="empty-state-desc" style={{ marginBottom: '24px' }}>
              The interactive decision center for approving, rejecting, or requesting additional evidence for triggered audits will be activated in Frontend Phase 2.
            </p>
            <div className="api-status" style={{ display: 'inline-flex', alignSelf: 'center' }}>
              <span>Phase 2 HITL Control Pending</span>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
