from closeio_api import Client

API_KEY = 'api_06w69rXjp1F3KOQmaShZ70.0tlaMFy2JA1gZhudoFGPMF'
api = Client(API_KEY)

try:
    leads = api.get('lead/', params={'_limit': 3})
    print("Successfully fetched leads:")
    for lead in leads['data']:
        print(f"- {lead.get('name', 'No Name')} (ID: {lead.get('id')})")
except Exception as e:
    print(f"Error fetching leads: {e}")
