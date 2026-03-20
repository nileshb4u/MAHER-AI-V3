"""
Database seeding script for MAHER AI
Initializes database with system agents
"""

from models import init_db, SessionLocal, Agent, AgentStatus

# System agents data
SYSTEM_AGENTS = [
    {
        'agent_id': 'geological-data-analyzer',
        'name': 'GeoInsight Assistant',
        'description': 'Analyzes geological survey data, identifies potential hydrocarbon reservoirs, and provides insights on subsurface structures.',
        'system_prompt': 'You are GeoInsight, an AI assistant specializing in geological data interpretation for oil and gas exploration. You process seismic data, well logs, and core sample reports to identify promising formations. Always present your findings with confidence levels and supporting evidence. Start by asking for the type of geological data to analyze.',
        'category': 'operations',
        'icon_svg': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>',
        'icon_background_color': '#14b8a6',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI'
    },
    {
        'agent_id': 'safety-incident-predictor',
        'name': 'SafeGuard AI Predictor',
        'description': 'Uses historical incident data and real-time operational parameters to predict potential safety hazards and recommend preventative actions.',
        'system_prompt': 'I am SafeGuard AI, a predictive safety assistant for industrial environments. My goal is to identify potential safety risks before they escalate into incidents. I analyze trends, operational conditions, and past events. Provide me with current operational data (e.g., equipment status, ongoing work permits, weather) and I will highlight areas of concern.',
        'category': 'safety',
        'icon_svg': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>',
        'icon_background_color': '#ef4444',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI'
    },
    {
        'agent_id': 'logistics-optimizer-bot',
        'name': 'LogiPro Route Optimizer',
        'description': 'Optimizes supply chain logistics for equipment and personnel transportation to and from remote sites, considering cost, time, and safety.',
        'system_prompt': 'You are LogiPro, an AI assistant for optimizing logistics in the energy sector. I help plan the most efficient and cost-effective routes for transporting materials, equipment, and personnel. Provide me with origin, destination, cargo details, and any constraints (e.g., deadlines, road closures, weather), and I will propose optimal solutions.',
        'category': 'operations',
        'icon_svg': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm12 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-8.25-3H17V9.75L19.25 12H6.75V6H15v2H8.75L6 10.75V15z"/></svg>',
        'icon_background_color': '#f97316',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI'
    },
    {
        'agent_id': 'regulatory-compliance-checker',
        'name': 'ReguCheck Advisor',
        'description': 'Cross-references project plans and operational procedures against current local and international regulations to ensure compliance.',
        'system_prompt': 'I am ReguCheck Advisor, an AI assistant dedicated to ensuring regulatory compliance in energy projects. Upload your project documentation or describe an operational procedure, and I will check it against relevant industry standards, environmental regulations, and safety codes. I can highlight potential non-compliance issues and suggest modifications.',
        'category': 'contracts',
        'icon_svg': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M19.48 6.02c-.3-.3-.79-.3-1.09 0L10 14.42l-4.39-4.39c-.3-.3-.79-.3-1.09 0s-.3.79 0 1.09l4.94 4.94c.15.15.34.22.54.22s.39-.07.54-.22l9.03-9.03c.29-.3.29-.79-.01-1.09zM3 20h18v-2H3v2zm0-4h18v-2H3v2zm0-4h18v-2H3v2z"/></svg>',
        'icon_background_color': '#4f46e5',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI'
    },
    {
        'agent_id': 'training-scenario-generator',
        'name': 'SimuLearn Trainer',
        'description': 'Generates realistic training scenarios for operators and maintenance crew, including emergency response and complex troubleshooting.',
        'system_prompt': 'Welcome to SimuLearn Trainer! I create dynamic and realistic training scenarios for personnel in high-risk industries. Specify the role (e.g., control room operator, field technician), the equipment involved, and the type of scenario (e.g., emergency shutdown, equipment malfunction, routine procedure), and I will generate a detailed simulation script.',
        'category': 'maintenance',
        'icon_svg': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3C7.03 3 3 7.03 3 12s4.03 9 9 9c1.09 0 2.13-.2 3.08-.54L17.5 23.5 20 21l-2.42-2.42C18.8 17.13 19 16.09 19 15c0-4.97-4.03-9-9-9zm0 16c-3.86 0-7-3.14-7-7s3.14-7 7-7 7 3.14 7 7-3.14 7-7 7zm1-11h-2v3H8v2h3v3h2v-3h3v-2h-3V8z"/></svg>',
        'icon_background_color': '#8b5cf6',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI'
    },
]

def seed_system_agents():
    """Seed database with system agents"""
    db = SessionLocal()

    try:
        print("Seeding system agents...")

        for agent_data in SYSTEM_AGENTS:
            # Check if agent already exists
            existing = db.query(Agent).filter(Agent.agent_id == agent_data['agent_id']).first()

            if existing:
                print(f"  ⚠️  Agent '{agent_data['name']}' already exists, skipping...")
                continue

            # Create new system agent
            agent = Agent(
                agent_id=agent_data['agent_id'],
                name=agent_data['name'],
                description=agent_data['description'],
                system_prompt=agent_data['system_prompt'],
                category=agent_data['category'],
                icon_svg=agent_data['icon_svg'],
                icon_background_color=agent_data['icon_background_color'],
                default_provider=agent_data['default_provider'],
                display_provider_name=agent_data['display_provider_name'],
                status=AgentStatus.PUBLISHED,
                is_system=True,
                created_by='system'
            )

            db.add(agent)
            print(f"  ✓ Added system agent: {agent_data['name']}")

        db.commit()
        print("\n✓ System agents seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Error seeding system agents: {e}")
        raise
    finally:
        db.close()

def main():
    """Main function to initialize and seed database"""
    print("=" * 60)
    print("MAHER AI - Database Initialization")
    print("=" * 60)
    print()

    # Initialize database (create tables)
    print("Initializing database...")
    init_db()
    print("✓ Database tables created\n")

    # Seed system agents
    seed_system_agents()

    print()
    print("=" * 60)
    print("Database setup complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
