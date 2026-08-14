import React from 'react';
import { ClipboardList } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';

export default function Reports() {
  return (
    <PageContainer 
      title="Synthesized Reports" 
      subtitle="View, verify, and export version-controlled finalized audit reports."
    >
      <div className="card">
        <div className="card-body">
          <div className="empty-state">
            <ClipboardList className="empty-state-icon" style={{ color: 'var(--accent-gold)' }} />
            <h3 className="empty-state-title">Final Audit Summaries</h3>
            <p className="empty-state-desc" style={{ marginBottom: '24px' }}>
              The report visualization viewer, version history comparison, and markdown exporter interfaces will be activated in Frontend Phase 2.
            </p>
            <div className="api-status" style={{ display: 'inline-flex', alignSelf: 'center' }}>
              <span>Phase 2 Analytics Pending</span>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
