from django.core.management.base import BaseCommand
from legal.models import LegalPage


class Command(BaseCommand):
    help = 'Create or update initial legal pages (Privacy Policy and Terms of Service)'

    def handle(self, *args, **options):
        self.stdout.write('Creating/updating legal pages...')

        # Privacy Policy Content
        privacy_content = """
<div class="privacy-intro">
    <h1>Privacy Policy</h1>
    <p class="effective-date"><strong>Effective Date: October 25, 2025</strong></p>
<p class="intro-text">This Privacy Policy describes how Real Estate Net collects, uses, and protects your personal information when you use our real estate platform.</p>
</div>

<div class="policy-section">
    <h2>1. Information You Collect</h2>
    <p>We collect various types of information to provide our real estate services effectively:</p>

    <div class="data-types">
        <h3><i class="fas fa-user"></i> Personal Information</h3>
        <ul>
            <li><strong>Name, Email, Phone:</strong> Account creation and communication</li>
            <li><strong>Address:</strong> Property-related services and geolocation features</li>
            <li><strong>User Account Details:</strong> Username, password, and profile information</li>
        </ul>

        <h3><i class="fas fa-home"></i> Property-Related Information</h3>
        <ul>
            <li><strong>Property Details:</strong> Listings, images, descriptions, pricing, and specifications</li>
            <li><strong>Property History:</strong> Viewing history, saved listings, and search preferences</li>
        </ul>

        <h3><i class="fas fa-chart-line"></i> Automatic Data</h3>
        <ul>
            <li><strong>IP Address:</strong> Website access and security monitoring</li>
            <li><strong>Browser Information:</strong> Device type, browser version, and operating system</li>
            <li><strong>Cookies and Tracking Data:</strong> Site usage analytics and performance monitoring</li>
            <li><strong>Location Data:</strong> Approximate location for localized property searches</li>
        </ul>
    </div>

    <p class="important-note"><em>We only collect data necessary for our core real estate services and user experience enhancement.</em></p>
</div>

<div class="policy-section">
    <h2>2. How We Use Your Information</h2>
    <p>Your information helps us provide and improve our real estate platform:</p>

    <h3><i class="fas fa-cogs"></i> Platform Services</h3>
    <ul>
        <li>Displaying and managing property listings for sale and lease</li>
        <li>Connecting property owners with potential buyers and agents</li>
        <li>Processing, verifying, and promoting property advertisements</li>
        <li>Sending property alerts and search notifications</li>
    </ul>

    <h3><i class="fas fa-star"></i> Premium Services</h3>
    <ul>
        <li>Managing premium membership subscriptions</li>
        <li>Providing advanced analytics and property performance insights</li>
        <li>Processing payment information for premium features</li>
        <li>Offering enhanced visibility and marketing tools</li>
    </ul>

    <h3><i class="fas fa-user-friends"></i> User Experience Enhancement</h3>
    <ul>
        <li>Personalizing property recommendations and search results</li>
        <li>Sending relevant property updates and market insights</li>
        <li>Improving site performance and technical functionality</li>
        <li>Providing customer support services</li>
    </ul>
</div>

<div class="policy-section">
    <h2>3. Sharing and Disclosure</h2>
    <p>We take your privacy seriously and only share information in specific circumstances:</p>

    <h3><i class="fas fa-server"></i> Service Providers</h3>
    <ul>
        <li><strong>Payment Processors:</strong> Stripe, PayPal for secure payment processing</li>
        <li><strong>Analytics Services:</strong> Google Analytics for website performance insights</li>
        <li><strong>Mapping Services:</strong> Google Maps for property location features</li>
    </ul>

    <h3><i class="fas fa-handshake"></i> Business Partners</h3>
    <ul>
        <li><strong>Verified Real Estate Agents:</strong> For property connections (with user consent)</li>
        <li><strong>Advertising Partners:</strong> For targeted property promotion</li>
        <li><strong>Verification Services:</strong> For property authenticity checks</li>
    </ul>

    <h3><i class="fas fa-gavel"></i> Legal Requirements</h3>
    <ul>
        <li><strong>Law Enforcement:</strong> When legally required by court orders or government requests</li>
        <li><strong>Fraud Prevention:</strong> To protect against fraudulent property listings or suspicious activities</li>
    </ul>

    <div class="important-note">
        <strong>Privacy Promise:</strong> We never sell your personal information to third parties for marketing purposes.
    </div>
</div>

<div class="policy-section">
    <h2>4. Cookies and Tracking</h2>
    <p>We use cookies and similar tracking technologies to enhance your experience:</p>

    <h3><i class="fas fa-cookie-bite"></i> Essential Cookies</h3>
    <ul>
        <li><strong>Session Management:</strong> Login sessions and user authentication</li>
        <li><strong>Security Features:</strong> Fraud prevention and account protection</li>
        <li><strong>Basic Functionality:</strong> Site navigation and feature access</li>
    </ul>

    <h3><i class="fas fa-chart-bar"></i> Analytics Cookies</h3>
    <ul>
        <li><strong>Google Analytics:</strong> Website usage statistics and performance monitoring</li>
        <li><strong>Search Behavior:</strong> Property search patterns and popular features</li>
        <li><strong>User Flow Analysis:</strong> Navigation paths and user engagement metrics</li>
    </ul>

    <h3><i class="fas fa-external-link-square-alt"></i> Third-Party Cookies</h3>
    <ul>
        <li><strong>Google Maps Cookies:</strong> For property map functionality</li>
        <li><strong>Social Media Widgets:</strong> For social sharing features</li>
        <li><strong>Advertising Cookies:</strong> For relevant property advertising (limited use)</li>
    </ul>

    <div class="cookie-control">
        <h4>Your Cookie Controls</h4>
        <p>You can control cookies through your browser settings:</p>
        <ul>
            <li>Disable cookies entirely (may limit some functionality)</li>
            <li>Clear existing cookies from our site</li>
            <li>Use private/incognito browsing mode</li>
        </ul>
    </div>
</div>

<div class="policy-section">
    <h2>5. Data Security</h2>
    <p>We implement industry-standard security measures to protect your information:</p>

    <h3><i class="fas fa-shield-alt"></i> Technical Safeguards</h3>
    <ul>
        <li><strong>SSL Encryption:</strong> All data transmitted securely over HTTPS</li>
        <li><strong>Data Encryption:</strong> Sensitive information stored in encrypted format</li>
        <li><strong>Regular Security Audits:</strong> Ongoing security testing and vulnerability assessments</li>
    </ul>

    <h3><i class="fas fa-lock"></i> Access Controls</h3>
    <ul>
        <li><strong>Limited Access:</strong> Only authorized personnel can access personal data</li>
        <li><strong>Role-Based Permissions:</strong> Different access levels based on job requirements</li>
        <li><strong>Activity Monitoring:</strong> Security logging and access tracking</li>
    </ul>

    <h3><i class="fas fa-database"></i> Data Protection Practices</h3>
    <ul>
        <li><strong>Regular Backups:</strong> Encrypted backups with secure storage</li>
        <li><strong>Incident Response:</strong> Prepared procedures for data breaches</li>
        <li><strong>Compliance Standards:</strong> Following GDPR and industry best practices</li>
    </ul>
</div>

<div class="policy-section">
    <h2>6. Your Rights</h2>
    <p>You have the following rights regarding your personal information:</p>

    <div class="rights-grid">
        <div class="rights-category">
            <h3><i class="fas fa-eye"></i> Access Rights</h3>
            <ul>
                <li><strong>View Your Data:</strong> Access all personal information we hold about you</li>
                <li><strong>Download Data:</strong> Request copies of your data in standard format</li>
                <li><strong>Portability:</strong> Transfer data to another service if technically feasible</li>
            </ul>
        </div>

        <div class="rights-category">
            <h3><i class="fas fa-edit"></i> Data Management Rights</h3>
            <ul>
                <li><strong>Correction:</strong> Update inaccurate or incomplete personal information</li>
                <li><strong>Deletion:</strong> Request deletion of your personal data (right to be forgotten)</li>
                <li><strong>Restriction:</strong> Limit processing of your data in certain circumstances</li>
                <li><strong>Objection:</strong> Object to processing for marketing or legitimate interests</li>
            </ul>
        </div>

        <div class="rights-category">
            <h3><i class="fas fa-bell"></i> Communication Preferences</h3>
            <ul>
                <li><strong>Unsubscribe:</strong> Opt-out of marketing communications at any time</li>
                <li><strong>Notification Settings:</strong> Control email and SMS notification preferences</li>
                <li><strong>Data Sharing:</strong> Opt-out of non-essential data sharing</li>
            </ul>
        </div>
    </div>
</div>

<div class="policy-section">
    <h2>7. Third-Party Services</h2>
    <p>Our platform may include links to external services:</p>

    <ul>
        <li><strong>Google Maps:</strong> Interactive property location maps</li>
        <li><strong>Real Estate Portals:</strong> Additional property information sources</li>
        <li><strong>Verification Services:</strong> Property documentation and validation</li>
        <li><strong>Financial Services:</strong> Mortgage calculators and financial tools</li>
    </ul>

    <div class="warning-note">
        <strong>Important:</strong> We are not responsible for the privacy practices or content of third-party websites. We encourage reviewing their privacy policies.
    </div>
</div>

<div class="policy-section">
    <h2>8. Children's Privacy</h2>
    <p>Our services are intended for adult real estate professionals and users:</p>
    <ul>
        <li>Users must be 18 years or older to create accounts</li>
        <li>We do not knowingly collect information from children under 18</li>
        <li>If we discover underage data collection, it will be deleted immediately</li>
    </ul>
</div>

<div class="policy-section">
    <h2>9. Policy Updates</h2>
    <p>We may update this Privacy Policy periodically:</p>

    <h3><i class="fas fa-sync"></i> Notification Process</h3>
    <ul>
        <li><strong>Date Updates:</strong> Last modified date at the top of this policy</li>
        <li><strong>Driver Changes:</strong> For major privacy practice changes</li>
        <li><strong>Continued Use:</strong> Continued service use implies policy acceptance</li>
    </ul>

    <h3><i class="fas fa-history"></i> Version Control</h3>
    <ul>
        <li><strong>Previous Versions:</strong> Maintained for transparency and reference</li>
        <li><strong>Archive Access:</strong> Contact us to access previous policy versions</li>
    </ul>
</div>

<div class="policy-section contact-section">
    <h2>10. Contact Information</h2>
    <p>For privacy concerns or questions, contact us:</p>

    <div class="contact-info">
        <div class="contact-item">
            <i class="fas fa-building"></i>
            <span><strong>Company Name:</strong> Real Estate Net</span>
        </div>
        <div class="contact-item">
            <i class="fas fa-envelope"></i>
            <span><strong>Support Email:</strong> support@realestatenet.com</span>
        </div>
        <div class="contact-item">
            <i class="fas fa-map-marker-alt"></i>
            <span><strong>Office Address:</strong> Real Estate Net</span>
        </div>
        <div class="contact-item">
            <i class="fas fa-globe"></i>
            <span><strong>Website:</strong> https://realestatenet.com</span>
        </div>
    </div>

    <hr>

    <div class="policy-footer">
        <em>This Privacy Policy was last updated on October 25, 2025.</em>
    </div>
</div>
"""

        terms_content = """
<div id="terms-content">
    <h1>&copy; Terms of Service</h1>
    <p class="terms-subtitle">Effortlessly explore property listings, connect with agents, and unlock premium features. Our platform provides a seamless real estate experience tailored to your needs.</p>
    <p class="effective-date"><strong>Effective Date: October 25, 2025</strong></p>
</div>

<div class="policy-section">
    <h2>1. 🤝 Acceptance of Terms</h2>
    <p>Welcome to Real Estate Net! By accessing or using our platform, you agree to be bound by these Terms of Service and our Privacy Policy. If you don't agree, please stop using our website immediately.</p>

    <div class="important-note">
        <strong>Key Point:</strong> Your continued use means you accept our terms and policies.
    </div>
</div>

<div class="policy-section">
    <h2>2. 🏠 Service Overview</h2>
    <p>Real Estate Net provides a comprehensive real estate platform designed to connect buyers, sellers, and professionals:</p>

    <div class="service-grid">
        <div class="service-category">
            <h3><i class="fas fa-tools"></i> Core Services</h3>
            <ul>
                <li><strong>Property Listings:</strong> Create, manage, and promote property listings</li>
                <li><strong>Search Tools:</strong> Advanced search and discovery features</li>
                <li><strong>Account Management:</strong> User profiles and account settings</li>
                <li><strong>Verification:</strong> Property authenticity and user verification</li>
            </ul>
        </div>

        <div class="service-category">
            <h3><i class="fas fa-star"></i> Premium Features</h3>
            <ul>
                <li><strong>Priority Placement:</strong> Higher visibility in search results</li>
                <li><strong>Analytics:</strong> Advanced property performance insights</li>
                <li><strong>Trust Indicators:</strong> Verified badges and credibility signals</li>
                <li><strong>Professional Tools:</strong> Agent and broker management features</li>
                <li><strong>Enhanced Marketing:</strong> Premium promotional capabilities</li>
            </ul>
        </div>
    </div>

    <p>We reserve the right to modify or discontinue any feature at any time without notice.</p>
</div>

<div class="policy-section">
    <h2>3. ✅ Eligibility Requirements</h2>
    <p>To use Real Estate Net, you must meet these basic requirements:</p>

    <h3><i class="fas fa-user-check"></i> Basic Requirements</h3>
    <ul>
        <li>Be at least 18 years old</li>
        <li>Have legal capacity to enter agreements</li>
        <li>Be a resident of Nepal or authorized real estate professional</li>
    </ul>

    <h3><i class="fas fa-id-badge"></i> Account Requirements</h3>
    <ul>
        <li>Provide accurate registration information</li>
        <li>Maintain account confidentiality</li>
        <li>Accept responsibility for account activities</li>
    </ul>
</div>

<div class="policy-section">
    <h2>4. 🔐 User Accounts</h2>
    <p>Your account is your responsibility. Please treat it carefully:</p>

    <h3><i class="fas fa-user-plus"></i> Creating Your Account</h3>
    <ul>
        <li>Valid email address and contact information</li>
        <li>Unique and secure password</li>
        <li>Complete required profile information</li>
    </ul>

    <h3><i class="fas fa-shield-alt"></i> Account Security</h3>
    <ul>
        <li>Report unauthorized access immediately</li>
        <li>Use strong passwords and enable 2FA</li>
        <li>You are responsible for all account activity</li>
    </ul>

    <h3><i class="fas fa-tools"></i> Account Management</h3>
    <ul>
        <li>Keep contact information current</li>
        <li>Regularly review account settings</li>
        <li>Report suspicious activity</li>
    </ul>

    <p>We may suspend accounts that violate our terms or appear suspicious.</p>
</div>

<div class="policy-section">
    <h2>5. 🏡 Property Listings</h2>
    <p>Your property listings should be accurate, complete, and compliant:</p>

    <h3><i class="fas fa-list-check"></i> Listing Requirements</h3>
    <ul>
        <li>Legal authority to list the property</li>
        <li>Accurate and truthful information</li>
        <li>High-quality photographs</li>
        <li>Compliance with all regulations</li>
    </ul>

    <h3><i class="fas fa-balance-scale"></i> Content Standards</h3>
    <ul>
        <li>No misleading information</li>
        <li>Respect intellectual property rights</li>
        <li>Include legal disclosures</li>
        <li>Follow fair housing laws</li>
    </ul>

    <h3><i class="fas fa-cog"></i> Listing Management</h3>
    <ul>
        <li>Listings may be removed for violations</li>
        <li>Regular monitoring for fraud</li>
        <li>Premium listing advantages</li>
        <li>Performance analytics available</li>
    </ul>
</div>

<div class="policy-section">
    <h2>6. 💎 Premium Services</h2>
    <p>Premium features enhance your real estate experience:</p>

    <h3><i class="fas fa-gift"></i> Premium Benefits</h3>
    <ul>
        <li>Priority search result placement</li>
        <li>Advanced property performance analytics</li>
        <li>Verified property badges</li>
        <li>Ad-free browsing experience</li>
        <li>Professional client management tools</li>
        <li>Enhanced marketing features</li>
    </ul>

    <h3><i class="fas fa-credit-card"></i> Billing & Payment</h3>
    <ul>
        <li>Secure third-party payment processing</li>
        <li>Fees charged in advance</li>
        <li>Non-refundable except by law</li>
        <li>Automatic renewal policy</li>
    </ul>

    <h3><i class="fas fa-times-circle"></i> Cancellation</h3>
    <ul>
        <li>Cancel through account settings</li>
        <li>Access continues until paid period ends</li>
        <li>No refunds for partial periods</li>
    </ul>
</div>

<div class="policy-section">
    <h2>7. 🚫 Prohibited Activities</h2>
    <p>Maintain a safe and fair environment for everyone:</p>

    <h3><i class="fas fa-file-alt"></i> Content Rules</h3>
    <ul>
        <li>No fake or misleading listings</li>
        <li>Copyright infringement prohibited</li>
        <li>No discriminatory or offensive content</li>
        <li>Spam content not allowed</li>
    </ul>

    <h3><i class="fas fa-bug"></i> Technical Restrictions</h3>
    <ul>
        <li>No hacking or security breaches</li>
        <li>Automated scraping prohibited</li>
        <li>Platform interference not allowed</li>
        <li>Bypassing restrictions forbidden</li>
    </ul>

    <h3><i class="fas fa-exclamation-triangle"></i> Business Ethics</h3>
    <ul>
        <li>Follow fair housing laws</li>
        <li>Illegal activities prohibited</li>
        <li>Accurate identification required</li>
        <li>Fraudulent transactions not permitted</li>
    </ul>
</div>

<div class="policy-section">
    <h2>8. © Intellectual Property</h2>
    <p>Respect intellectual property rights on our platform:</p>

    <h3><i class="fas fa-copyright"></i> Our Rights</h3>
    <ul>
        <li>Website design and code protected</li>
        <li>Branding and trademarks reserved</li>
        <li>Content and database rights apply</li>
        <li>Proprietary information restricted</li>
    </ul>

    <h3><i class="fas fa-upload"></i> Your Content</h3>
    <ul>
        <li>You retain your uploaded content rights</li>
        <li>Grant non-exclusive platform license</li>
        <li>Content must not violate others' rights</li>
        <li>Terms govern content usage</li>
    </ul>

    <h3><i class="fas fa-hand-paper"></i> Permitted Usage</h3>
    <ul>
        <li>Personal, non-commercial use allowed</li>
        <li>Attribution when sharing required</li>
        <li>Written permission for reproduction</li>
        <li>Copyright and trademark compliance</li>
    </ul>
</div>

<div class="policy-section">
    <h2>9. ⚖️ Liability Limitations</h2>
    <p>Understand our service limitations and your responsibilities:</p>

    <h3><i class="fas fa-info-circle"></i> Service Limitations</h3>
    <ul>
        <li>No guarantee of transaction completion</li>
        <li>Platform availability not guaranteed</li>
        <li>No warranty on all property information</li>
        <li>Third-party services as provided</li>
    </ul>

    <h3><i class="fas fa-exclamation-circle"></i> Exclusions</h3>
    <ul>
        <li>Not liable for transaction outcomes</li>
        <li>No responsibility for third-party actions</li>
        <li>Limited data loss liability</li>
        <li>No indirect damage liability</li>
    </ul>

    <h3><i class="fas fa-user-shield"></i> User Responsibilities</h3>
    <ul>
        <li>Independent property verification</li>
        <li>Proper platform usage</li>
        <li>Maintain emergency contact info</li>
        <li>Legal compliance required</li>
    </ul>
</div>

<div class="policy-section">
    <h2>10. 🚪 Account Termination</h2>
    <p>understand when and how accounts may be terminated:</p>

    <h3><i class="fas fa-power-off"></i> Platform Rights</h3>
    <ul>
        <li>Accounts may be suspended anytime</li>
        <li>Immediate termination for violations</li>
        <li>Data deletion after retention period</li>
        <li>Reasonable termination procedures</li>
    </ul>

    <h3><i class="fas fa-procedures"></i> Termination Process</h3>
    <ul>
        <li>Written notice when possible</li>
        <li>Appeal process for disputes</li>
        <li>Data handling according to policies</li>
        <li>Post-termination obligations remain</li>
    </ul>
</div>

<div class="policy-section">
    <h2>11. 🔗 Third-Party Services</h2>
    <p>We integrate with external services and tools:</p>

    <h3><i class="fas fa-external-link-square-alt"></i> Integrations</h3>
    <ul>
        <li><strong>Google Maps:</strong> Location and mapping services</li>
        <li><strong>Payment Processors:</strong> Stripe, PayPal for transactions</li>
        <li><strong>Social Platforms:</strong> Sharing and verification</li>
        <li><strong>APIs:</strong> Verification and external services</li>
        <li><strong>Financial Tools:</strong> Calculators and market data</li>
    </ul>

    <h3><i class="fas fa-file-contract"></i> Third-Party Terms</h3>
    <ul>
        <li>Each service has its own terms</li>
        <li>We don't control third-party services</li>
        <li>Review external policies yourself</li>
        <li>Our liability is limited to integration</li>
    </ul>
</div>

<div class="policy-section">
    <h2>12. 🔄 Terms Updates</h2>
    <p>These terms may evolve with our platform:</p>

    <h3><i class="fas fa-sync-alt"></i> Update Process</h3>
    <ul>
        <li>Periodic review and updates</li>
        <li>Clear effective dates</li>
        <li>Automatic application to users</li>
        <li>Continued use means acceptance</li>
    </ul>

    <h3><i class="fas fa-user-edit"></i> User Responsibilities</h3>
    <ul>
        <li>Regularly review updated terms</li>
        <li>Contact support for clarification</li>
        <li>Termination option if terms unacceptable</li>
        <li>Legal compliance required</li>
    </ul>
</div>

<div class="policy-section contact-section">
    <h2>13. 📞 Contact Information</h2>
    <p>Have questions or concerns about these terms? Contact us:</p>

    <div class="contact-info">
        <div class="contact-item">
            <i class="fas fa-building"></i>
            <span><strong>Company Name:</strong> Real Estate Net</span>
        </div>
        <div class="contact-item">
            <i class="fas fa-envelope"></i>
            <span><strong>Support Email:</strong> support@realestatenet.com</span>
        </div>
        <div class="contact-item">
            <i class="fas fa-globe"></i>
            <span><strong>Website:</strong> https://realestatenet.com</span>
        </div>
        <div class="contact-item">
            <i class="fas fa-map-marker-alt"></i>
            <span><strong>Office Address:</strong> Real Estate Net, Nepal</span>
        </div>
    </div>

    <hr>

    <div class="policy-footer">
        <em>Thank you for being part of the Real Estate Net community!</em>
        <br>
        <strong>Last updated: October 25, 2025</strong>
    </div>
</div>
"""

        # Create or update Privacy Policy
        privacy_policy, created_privacy = LegalPage.objects.get_or_create(
            slug='privacy-policy',
            defaults={
                'title': 'Privacy Policy',
                'content': privacy_content
            }
        )
        if not created_privacy:
            privacy_policy.content = privacy_content
            privacy_policy.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated existing Privacy Policy')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Created new Privacy Policy')
            )

        # Create or update Terms of Service
        terms_service, created_terms = LegalPage.objects.get_or_create(
            slug='terms-of-service',
            defaults={
                'title': 'Terms of Service',
                'content': terms_content
            }
        )
        if not created_terms:
            terms_service.content = terms_content
            terms_service.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated existing Terms of Service')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Created new Terms of Service')
            )

        self.stdout.write(
            self.style.SUCCESS('\nLegal pages created/updated successfully!')
        )
        self.stdout.write(
            '  📄 Privacy Policy: /legal/privacy-policy/'
        )
        self.stdout.write(
            '  ⚖️  Terms of Service: /legal/terms-of-service/'
        )
