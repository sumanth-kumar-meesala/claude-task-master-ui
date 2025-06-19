/**
 * Project Overview Display - Shows generated project documentation
 */

import React, { useState } from 'react';
import { 
  DocumentTextIcon,
  BuildingOffice2Icon,
  ClockIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  UserGroupIcon,
  PrinterIcon,
  ShareIcon,
  PencilIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';

interface ProjectOverview {
  id: string;
  executive_summary: string;
  technical_architecture: string;
  implementation_plan: string;
  risk_assessment: string;
  resource_requirements: string;
  timeline_estimate: string;
  success_metrics: string;
  generated_by: string[];
  generated_at: string;
  confidence_score: number;
}

interface ProjectOverviewDisplayProps {
  overview: ProjectOverview;
  projectName: string;
  onEdit?: (section: string) => void;
  onExport?: (format: 'pdf' | 'docx' | 'md') => void;
}

export const ProjectOverviewDisplay: React.FC<ProjectOverviewDisplayProps> = ({
  overview,
  projectName,
  onEdit,
  onExport
}) => {
  const [activeSection, setActiveSection] = useState<string>('executive_summary');

  const sections = [
    {
      id: 'executive_summary',
      title: 'Executive Summary',
      icon: DocumentTextIcon,
      content: overview.executive_summary,
      description: 'High-level project overview and business value'
    },
    {
      id: 'technical_architecture',
      title: 'Technical Architecture',
      icon: BuildingOffice2Icon,
      content: overview.technical_architecture,
      description: 'System design and technology stack'
    },
    {
      id: 'implementation_plan',
      title: 'Implementation Plan',
      icon: ClockIcon,
      content: overview.implementation_plan,
      description: 'Detailed project phases and milestones'
    },
    {
      id: 'risk_assessment',
      title: 'Risk Assessment',
      icon: ExclamationTriangleIcon,
      content: overview.risk_assessment,
      description: 'Potential risks and mitigation strategies'
    },
    {
      id: 'resource_requirements',
      title: 'Resource Requirements',
      icon: CurrencyDollarIcon,
      content: overview.resource_requirements,
      description: 'Team, budget, and infrastructure needs'
    },
    {
      id: 'timeline_estimate',
      title: 'Timeline Estimate',
      icon: ClockIcon,
      content: overview.timeline_estimate,
      description: 'Project schedule and delivery dates'
    },
    {
      id: 'success_metrics',
      title: 'Success Metrics',
      icon: ChartBarIcon,
      content: overview.success_metrics,
      description: 'KPIs and measurement criteria'
    }
  ];

  const getConfidenceBadge = (score: number) => {
    if (score >= 80) return 'badge-success';
    if (score >= 60) return 'badge-warning';
    return 'badge-error';
  };

  const formatContent = (content: string) => {
    // Simple formatting for better readability
    return content
      .split('\n')
      .map((paragraph, index) => (
        <p key={index} className="mb-3 text-base-content/80 leading-relaxed">
          {paragraph.trim()}
        </p>
      ));
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{projectName} - Project Overview</h1>
              <div className="flex items-center gap-4 text-sm text-base-content/70">
                <span>Generated on {new Date(overview.generated_at).toLocaleDateString()}</span>
                <span>•</span>
                <span>By {overview.generated_by.length} AI agents</span>
                <span>•</span>
                <div className="flex items-center gap-2">
                  <span>Confidence:</span>
                  <div className={`badge ${getConfidenceBadge(overview.confidence_score)}`}>
                    {overview.confidence_score}%
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <div className="dropdown dropdown-end">
                <label tabIndex={0} className="btn btn-outline btn-sm">
                  <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                  Export
                </label>
                <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                  <li><a onClick={() => onExport?.('pdf')}>Export as PDF</a></li>
                  <li><a onClick={() => onExport?.('docx')}>Export as Word</a></li>
                  <li><a onClick={() => onExport?.('md')}>Export as Markdown</a></li>
                </ul>
              </div>
              
              <button className="btn btn-outline btn-sm">
                <ShareIcon className="w-4 h-4 mr-2" />
                Share
              </button>
              
              <button className="btn btn-outline btn-sm">
                <PrinterIcon className="w-4 h-4 mr-2" />
                Print
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1">
          <div className="card bg-base-100 shadow-lg sticky top-6">
            <div className="card-body p-4">
              <h3 className="font-semibold mb-4">Sections</h3>
              <ul className="menu menu-compact">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <li key={section.id}>
                      <a
                        className={`${activeSection === section.id ? 'active' : ''}`}
                        onClick={() => setActiveSection(section.id)}
                      >
                        <Icon className="w-4 h-4" />
                        <div>
                          <div className="font-medium">{section.title}</div>
                          <div className="text-xs text-base-content/60">{section.description}</div>
                        </div>
                      </a>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3">
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              {sections.map((section) => {
                if (section.id !== activeSection) return null;
                
                const Icon = section.icon;
                
                return (
                  <div key={section.id} className="space-y-6">
                    {/* Section Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Icon className="w-6 h-6 text-primary" />
                        <div>
                          <h2 className="text-2xl font-bold">{section.title}</h2>
                          <p className="text-base-content/70">{section.description}</p>
                        </div>
                      </div>
                      
                      {onEdit && (
                        <button
                          onClick={() => onEdit(section.id)}
                          className="btn btn-ghost btn-sm"
                        >
                          <PencilIcon className="w-4 h-4 mr-2" />
                          Edit
                        </button>
                      )}
                    </div>

                    {/* Section Content */}
                    <div className="prose prose-lg max-w-none">
                      {section.content ? (
                        formatContent(section.content)
                      ) : (
                        <div className="text-center py-8">
                          <Icon className="w-12 h-12 mx-auto text-base-content/30 mb-4" />
                          <p className="text-base-content/70">
                            This section was not generated. Try regenerating the overview with appropriate agents.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Generation Info */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <UserGroupIcon className="w-5 h-5" />
            Generation Details
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="stat">
              <div className="stat-title">Generated By</div>
              <div className="stat-value text-lg">{overview.generated_by.length} Agents</div>
              <div className="stat-desc">
                {overview.generated_by.map(agent => agent.replace('_', ' ')).join(', ')}
              </div>
            </div>
            
            <div className="stat">
              <div className="stat-title">Confidence Score</div>
              <div className="stat-value text-lg">{overview.confidence_score}%</div>
              <div className="stat-desc">
                {overview.confidence_score >= 80 ? 'High confidence' :
                 overview.confidence_score >= 60 ? 'Medium confidence' : 'Low confidence'}
              </div>
            </div>
            
            <div className="stat">
              <div className="stat-title">Generated On</div>
              <div className="stat-value text-lg">
                {new Date(overview.generated_at).toLocaleDateString()}
              </div>
              <div className="stat-desc">
                {new Date(overview.generated_at).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quality Indicators */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          <h3 className="font-semibold mb-4">Quality Assessment</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {sections.map((section) => {
              const hasContent = section.content && section.content.trim().length > 0;
              const contentLength = section.content?.length || 0;
              const quality = contentLength > 500 ? 'high' : contentLength > 200 ? 'medium' : 'low';
              
              return (
                <div key={section.id} className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    !hasContent ? 'bg-error' :
                    quality === 'high' ? 'bg-success' :
                    quality === 'medium' ? 'bg-warning' : 'bg-error'
                  }`} />
                  <div>
                    <div className="font-medium text-sm">{section.title}</div>
                    <div className="text-xs text-base-content/60">
                      {!hasContent ? 'Missing' :
                       quality === 'high' ? 'Comprehensive' :
                       quality === 'medium' ? 'Basic' : 'Minimal'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
