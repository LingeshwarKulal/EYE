"""  
EYE - HTML Report Generator
Creates professional security assessment reports
"""
import os
from datetime import datetime
from typing import Dict, Any
from jinja2 import Template
from rich.console import Console

console = Console()


class HTMLReporter:
    """
    Generates professional HTML security reports
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, scan_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive HTML security report
        
        Args:
            scan_data: Complete scan results dictionary
            
        Returns:
            Path to generated HTML report
        """
        # Extract statistics
        stats = scan_data.get('statistics', {})
        target = scan_data.get('target_domain', 'Unknown')
        
        # Prepare data for template
        template_data = {
            'target_domain': target,
            'scan_date': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            'statistics': stats,
            'subdomains': scan_data.get('subdomains', []),
            'scan_results': scan_data.get('scan_results', []),
            'os_detection': scan_data.get('os_detection', {}),
            'technology_stack': scan_data.get('technology_stack', {}),
            'sensitive_files': scan_data.get('sensitive_files', []),
            'harvest_data': scan_data.get('harvest_data', {}),
            'social_profiles': scan_data.get('social_profiles', {}),
            'cors_vulnerabilities': scan_data.get('cors_vulnerabilities', []),
            'security_audit': scan_data.get('security_audit', {}),
            'redteam_actuators': scan_data.get('redteam_actuators', {}),
            'redteam_bypasses': scan_data.get('redteam_bypasses', {})
        }
        
        # Calculate risk level
        risk_score = self._calculate_risk_score(scan_data)
        template_data['risk_level'] = self._get_risk_level(risk_score)
        template_data['risk_score'] = risk_score
        
        # Render HTML template
        html_content = self._render_template(template_data)
        
        # Save report
        report_path = os.path.join(self.output_dir, 'security_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _calculate_risk_score(self, scan_data: Dict[str, Any]) -> int:
        """Calculate overall risk score (0-100)"""
        score = 0
        stats = scan_data.get('statistics', {})
        
        # Sensitive files (up to 40 points)
        sensitive_count = stats.get('sensitive_files', 0)
        score += min(sensitive_count * 10, 40)
        
        # Actuators (up to 30 points)
        actuator_count = stats.get('actuators_found', 0)
        score += min(actuator_count * 10, 30)
        
        # Access control bypasses (up to 20 points)
        bypass_count = stats.get('successful_bypasses', 0)
        score += min(bypass_count * 10, 20)
        
        # CORS issues (up to 10 points)
        cors_count = stats.get('cors_vulnerabilities', 0)
        score += min(cors_count * 5, 10)
        
        return min(score, 100)
    
    def _get_risk_level(self, score: int) -> Dict[str, str]:
        """Determine risk level from score"""
        if score >= 70:
            return {'level': 'CRITICAL', 'color': '#dc3545', 'emoji': '🔴'}
        elif score >= 40:
            return {'level': 'HIGH', 'color': '#fd7e14', 'emoji': '🟠'}
        elif score >= 20:
            return {'level': 'MEDIUM', 'color': '#ffc107', 'emoji': '🟡'}
        else:
            return {'level': 'LOW', 'color': '#28a745', 'emoji': '🟢'}
    
    def _render_template(self, data: Dict[str, Any]) -> str:
        """Render HTML template with Jinja2"""
        
        template_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EYE Security Report - {{ target_domain }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 30px;
        }
        
        .section:last-child {
            border-bottom: none;
        }
        
        .section h2 {
            color: #1e3c72;
            font-size: 1.8em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
            background-color: {{ risk_level.color }};
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .stat-card .label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .ai-summary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
            white-space: pre-wrap;
            line-height: 1.8;
        }
        
        .findings-list {
            list-style: none;
        }
        
        .findings-list li {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
        }
        
        .findings-list li.medium {
            border-left-color: #ffc107;
        }
        
        .findings-list li.low {
            border-left-color: #28a745;
        }
        
        .findings-list li.critical {
            border-left-color: #dc3545;
            background: #fff5f5;
        }
        
        .code {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        table th {
            background: #1e3c72;
            color: white;
            padding: 12px;
            text-align: left;
        }
        
        table td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        
        table tr:hover {
            background: #f8f9fa;
        }
        
        .footer {
            background: #2d3748;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }
        
        .severity-critical { color: #dc3545; font-weight: bold; }
        .severity-high { color: #fd7e14; font-weight: bold; }
        .severity-medium { color: #ffc107; font-weight: bold; }
        .severity-low { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 EYE Security Report</h1>
            <p class="subtitle">Automated Attack Surface Assessment</p>
            <p style="margin-top: 15px; font-size: 1.1em;">
                Target: <strong>{{ target_domain }}</strong><br>
                Generated: {{ scan_date }}
            </p>
        </div>
        
        <div class="content">
            <!-- Risk Assessment -->
            <div class="section">
                <h2>⚠️ Risk Assessment</h2>
                <p style="margin: 20px 0;">
                    Overall Risk Level: <span class="risk-badge">{{ risk_level.emoji }} {{ risk_level.level }}</span>
                    <span style="margin-left: 20px;">Risk Score: <strong>{{ risk_score }}/100</strong></span>
                </p>
            </div>
            
            <!-- Statistics Overview -->
            <div class="section">
                <h2>📊 Statistics Overview</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="label">Subdomains</div>
                        <div class="number">{{ statistics.total_subdomains }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Active Hosts</div>
                        <div class="number">{{ statistics.active_hosts }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Open Ports</div>
                        <div class="number">{{ statistics.total_open_ports }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Sensitive Files</div>
                        <div class="number">{{ statistics.sensitive_files }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Actuators Found</div>
                        <div class="number">{{ statistics.actuators_found }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Bypasses</div>
                        <div class="number">{{ statistics.successful_bypasses }}</div>
                    </div>
                </div>
            </div>
            
            <!-- Sensitive Files -->
            {% if sensitive_files %}
            <div class="section">
                <h2>🔥 Sensitive Files Exposed</h2>
                <ul class="findings-list">
                {% for file in sensitive_files %}
                    <li class="{{ file.severity|lower }}">
                        <strong class="severity-{{ file.severity|lower }}">{{ file.severity }}</strong> - 
                        <span class="code">{{ file.url }}</span><br>
                        Status: {{ file.status }}
                    </li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            <!-- Spring Boot Actuators -->
            {% if statistics.actuators_found > 0 %}
            <div class="section">
                <h2>🔴 Spring Boot Actuators</h2>
                <ul class="findings-list">
                {% for url, data in redteam_actuators.items() %}
                    {% for actuator in data.actuators_found %}
                    <li class="critical">
                        <strong class="severity-{{ actuator.severity|lower }}">{{ actuator.severity }}</strong> - 
                        <span class="code">{{ actuator.endpoint }}</span><br>
                        Host: {{ url }}<br>
                        Status: {{ actuator.status }}
                    </li>
                    {% endfor %}
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            <!-- Access Control Bypasses -->
            {% if statistics.successful_bypasses > 0 %}
            <div class="section">
                <h2>🔓 Access Control Bypasses</h2>
                <ul class="findings-list">
                {% for url, data in redteam_bypasses.items() %}
                    {% if data.bypassed %}
                    <li class="critical">
                        <strong>BYPASSED:</strong> <span class="code">{{ url }}</span><br>
                        Original Status: {{ data.original_status }} → Bypass Status: {{ data.bypass_status }}<br>
                        Technique: <strong>{{ data.technique }}</strong>
                    </li>
                    {% endif %}
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            <!-- CORS Vulnerabilities -->
            {% if cors_vulnerabilities %}
            <div class="section">
                <h2>🔴 CORS Misconfigurations</h2>
                <ul class="findings-list">
                {% for vuln in cors_vulnerabilities %}
                    <li class="critical">
                        <span class="code">{{ vuln.url }}</span><br>
                        Headers: {{ vuln.headers }}
                    </li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            <!-- Port Scan Results -->
            <div class="section">
                <h2>🔍 Port Scan Results & System Information</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Host</th>
                            <th>Operating System</th>
                            <th>Open Ports</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for result in scan_results %}
                        {% if result.open_ports %}
                        <tr>
                            <td>{{ result.host }}</td>
                            <td>
                                {% if os_detection.get(result.host) %}
                                    {{ os_detection[result.host].os_guess }}
                                    {% if os_detection[result.host].ttl %}
                                        <br><small style="color: #666;">TTL: {{ os_detection[result.host].ttl }}</small>
                                    {% endif %}
                                {% else %}
                                    <span style="color: #999;">N/A</span>
                                {% endif %}
                            </td>
                            <td>{{ result.open_ports|join(', ') }}</td>
                            <td>✅ Active</td>
                        </tr>
                        {% endif %}
                    {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <!-- Technology Stack -->
            {% if technology_stack %}
            <div class="section">
                <h2>🔧 Technology Stack Detection</h2>
                <table>
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>Server</th>
                            <th>CMS/Framework</th>
                            <th>Language</th>
                            <th>CDN/WAF</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for url, tech in technology_stack.items() %}
                        {% if not tech.get('error') %}
                        <tr>
                            <td>{{ url }}</td>
                            <td>{{ tech.server or 'Unknown' }}</td>
                            <td>
                                {% if tech.cms %}
                                    <strong>CMS:</strong> {{ tech.cms|join(', ') }}<br>
                                {% endif %}
                                {% if tech.frameworks %}
                                    <strong>Framework:</strong> {{ tech.frameworks|join(', ') }}
                                {% endif %}
                                {% if not tech.cms and not tech.frameworks %}
                                    <span style="color: #999;">N/A</span>
                                {% endif %}
                            </td>
                            <td>{{ tech.languages|join(', ') if tech.languages else 'N/A' }}</td>
                            <td>
                                {% if tech.cdn %}
                                    <strong>CDN:</strong> {{ tech.cdn }}<br>
                                {% endif %}
                                {% if tech.waf %}
                                    <strong>WAF:</strong> {{ tech.waf }}
                                {% endif %}
                                {% if not tech.cdn and not tech.waf %}
                                    <span style="color: #999;">None</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endif %}
                    {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            <!-- Data Harvest -->
            {% if statistics.emails_found > 0 or statistics.phones_found > 0 %}
            <div class="section">
                <h2>📧 Data Exposure</h2>
                <p><strong>Total Emails Found:</strong> {{ statistics.emails_found }}</p>
                <p><strong>Total Phone Numbers Found:</strong> {{ statistics.phones_found }}</p>
                <p style="margin-top: 15px; color: #666;">
                    <em>Full details available in JSON/CSV export files.</em>
                </p>
            </div>
            {% endif %}
            
            <!-- Social Profiles -->
            {% if statistics.social_profiles_found > 0 %}
            <div class="section">
                <h2>🔗 Social Media Profiles</h2>
                <p><strong>Total Profiles Found:</strong> {{ statistics.social_profiles_found }}</p>
                <p style="margin-top: 15px; color: #666;">
                    <em>Full details available in JSON/CSV export files.</em>
                </p>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>🔍 Generated by <strong>EYE - Automated Attack Surface Manager</strong></p>
            <p>Created by John Ripper | Stay Ethical</p>
        </div>
    </div>
</body>
</html>
"""
        
        template = Template(template_html)
        return template.render(**data)
