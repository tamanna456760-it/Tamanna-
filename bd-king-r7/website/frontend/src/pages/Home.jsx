import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Zap, Shield, Globe, Users, Rocket } from "lucide-react";
import "./Home.css";

const Home = () => {
  const features = [
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Get instant responses with our optimized AI model",
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your conversations are encrypted and never stored",
    },
    {
      icon: Globe,
      title: "Multi-Language",
      description: "Communicate in over 50 languages seamlessly",
    },
    {
      icon: Users,
      title: "Collaborative",
      description: "Share conversations and work together in real-time",
    },
    {
      icon: Rocket,
      title: "Always Learning",
      description: "Continuously improved with the latest AI advancements",
    },
  ];

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                Meet <span className="gradient-text">BD-King-R7</span>
              </h1>
              <p className="hero-description">
                Your advanced AI companion for intelligent conversations,
                creative tasks, and complex problem-solving. Powered by
                cutting-edge artificial intelligence.
              </p>
              <div className="hero-actions">
                <Link to="/chat" className="btn btn-primary">
                  Start Chatting <ArrowRight size={20} />
                </Link>
                <Link to="/features" className="btn btn-secondary">
                  Learn More
                </Link>
              </div>
            </div>
            <div className="hero-visual">
              <div className="ai-orb">
                <div className="orb-core"></div>
                <div className="orb-ring orb-ring-1"></div>
                <div className="orb-ring orb-ring-2"></div>
                <div className="orb-ring orb-ring-3"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Why Choose BD-King-R7?</h2>
          <div className="features-grid">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="feature-card">
                  <div className="feature-icon">
                    <Icon size={32} />
                  </div>
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2 className="cta-title">Ready to Experience the Future of AI?</h2>
            <p className="cta-description">
              Join thousands of users who are already enhancing their
              productivity with BD-King-R7.
            </p>
            <Link to="/chat" className="btn btn-primary btn-large">
              Start Your Journey <Rocket size={20} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
