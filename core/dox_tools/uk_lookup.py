import json

try:
    import urllib.request
    import urllib.parse
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class _Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        MAGENTA = '\033[95m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    Fore = _Fore()


def _print_header(title):
    print(f"\n{Fore.CYAN}{'='*70}{Fore.RESET}")
    print(f"{Fore.WHITE}{title}{Fore.RESET}")
    print(f"{Fore.CYAN}{'='*70}{Fore.RESET}\n")


def _fetch_json(url, api_key=None):
    try:
        req = urllib.request.Request(url)
        if api_key:
            req.add_header('Authorization', f'Bearer {api_key}')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return None


def _validate_postcode(postcode):
    postcode = postcode.upper().replace(' ', '')
    import re
    pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][A-Z]{2}$'
    return re.match(pattern, postcode) is not None


def run_uk_address_lookup():
    _print_header("UK ADDRESS LOOKUP // POSTCODE SEARCH")

    postcode = input(f"{Fore.MAGENTA}[?] Enter UK postcode (e.g. SW1A 1AA): {Fore.RESET}").strip()
    postcode = postcode.upper().replace(' ', '')

    if not postcode:
        print(f"{Fore.RED}[!] No postcode entered.{Fore.RESET}")
        input(f"{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
        return

    if not _validate_postcode(postcode):
        print(f"{Fore.YELLOW}[!] Invalid postcode format. Attempting lookup anyway...{Fore.RESET}")

    url = f"https://api.postcodes.io/postcodes/{postcode}"
    data = _fetch_json(url)

    if data is None:
        print(f"{Fore.RED}[!] Failed to fetch data. Check postcode or network.{Fore.RESET}")
        input(f"{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
        return

    if data.get('status') == 404 or data.get('error'):
        print(f"{Fore.RED}[!] Postcode not found: {data.get('error', 'Unknown error')}{Fore.RESET}")
        input(f"{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
        return

    result = data.get('result', {})

    print(f"\n{Fore.GREEN}--- POSTCODE INFORMATION ---{Fore.RESET}")
    print(f"  {Fore.CYAN}Postcode:{Fore.RESET} {result.get('postcode', 'N/A')}")
    print(f"  {Fore.CYAN}Area:{Fore.RESET} {result.get('admin_district', 'N/A')}")
    print(f"  {Fore.CYAN}District:{Fore.RESET} {result.get('admin_district', 'N/A')}")
    print(f"  {Fore.CYAN}Ward:{Fore.RESET} {result.get('admin_ward', 'N/A')}")
    print(f"  {Fore.CYAN}Country:{Fore.RESET} {result.get('country', 'N/A')}")
    print(f"  {Fore.CYAN}Region:{Fore.RESET} {result.get('region', 'N/A')}")
    print(f"  {Fore.CYAN}Coordinates:{Fore.RESET} {result.get('latitude', 'N/A')}, {result.get('longitude', 'N/A')}")

    lat = result.get('latitude')
    lon = result.get('longitude')

    if lat and lon:
        nearest_url = f"https://api.postcodes.io/postcodes?ltrs={postcode}&limit=5"
        nearest_data = _fetch_json(nearest_url)
        if nearest_data and nearest_data.get('result'):
            print(f"\n  {Fore.GREEN}Nearby postcodes:{Fore.RESET}")
            for i, np in enumerate(nearest_data['result'][:5], 1):
                print(f"    {i}. {np.get('postcode', '')} ({np.get('admin_district', '')})")

    print(f"\n{Fore.GREEN}--- LOCATION CONTEXT ---{Fore.RESET}")
    print(f"  {Fore.CYAN}Admin County:{Fore.RESET} {result.get('admin_county', 'N/A')}")
    print(f"  {Fore.CYAN}Admin Ward:{Fore.RESET} {result.get('admin_ward', 'N/A')}")
    print(f"  {Fore.CYAN}Civil Parish:{Fore.RESET} {result.get('parish', 'N/A')}")

    parishes_url = f"https://api.postcodes.io/postcodes/{postcode}/postcodes"
    print(f"\n{Fore.CYAN}[*] For resident/staff lookups at this address, use Companies House search with the postcode.{Fore.RESET}")

    input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")


def run_uk_name_search():
    _print_header("UK NAME SEARCH // COMPANIES HOUSE")

    print(f"{Fore.YELLOW}[*] This searches Companies House for person/company records.{Fore.RESET}")
    print(f"{Fore.YELLOW}[*] Requires a free Companies House API key.{Fore.RESET}")
    print(f"{Fore.YELLOW}[*] Get one at: {Fore.CYAN}https://developer.company-information.service.gov.uk{Fore.RESET}\n")

    api_key = input(f"{Fore.MAGENTA}[?] Companies House API key: {Fore.RESET}").strip()
    if not api_key:
        print(f"{Fore.RED}[!] API key required for UK name search.{Fore.RESET}")
        input(f"{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
        return

    search_term = input(f"{Fore.MAGENTA}[?] Enter name to search: {Fore.RESET}").strip()
    if not search_term:
        print(f"{Fore.RED}[!] No name entered.{Fore.RESET}")
        input(f"{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
        return

    encoded = urllib.parse.quote(search_term)
    url = f"https://api.company-information.service.gov.uk/search/officers?q={encoded}&limit=20"
    data = _fetch_json(url, api_key=api_key)

    if data is None:
        print(f"{Fore.RED}[!] Failed to fetch data. Check API key and network.{Fore.RESET}")
        input(f"{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
        return

    items = data.get('items', [])
    if not items:
        print(f"{Fore.YELLOW}[*] No results found for '{search_term}'.{Fore.RESET}")
        input(f"\n{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
        return

    print(f"\n{Fore.GREEN}Found {data.get('total', len(items))} result(s) for '{search_term}':{Fore.RESET}\n")

    for i, item in enumerate(items, 1):
        name = item.get('name', 'N/A')
        company = item.get('appointed_to', {}).get('company_name', 'N/A')
        position = item.get('position', 'N/A')
        appointed = item.get('appointed_on', 'N/A')

        addresses = item.get('address', {})
        addr_parts = []
        for key in ['address_line_1', 'address_line_2', 'locality', 'region', 'postal_code', 'country', 'po_box']:
            val = addresses.get(key)
            if val:
                addr_parts.append(val)
        address_str = ', '.join(addr_parts) if addr_parts else 'N/A'

        print(f"  {Fore.CYAN}[{i}]{Fore.RESET} {Fore.WHITE}{name}{Fore.RESET}")
        print(f"      {Fore.YELLOW}Company:{Fore.RESET} {company}")
        print(f"      {Fore.YELLOW}Position:{Fore.RESET} {position}")
        print(f"      {Fore.YELLOW}Appointed:{Fore.RESET} {appointed}")
        print(f"      {Fore.YELLOW}Address:{Fore.RESET} {address_str}")

        company_number = item.get('appointed_to', {}).get('company_number')
        if company_number:
            detail_url = f"https://api.company-information.service.gov.uk/company/{company_number}"
            detail = _fetch_json(detail_url, api_key=api_key)
            if detail:
                print(f"      {Fore.YELLOW}Company Number:{Fore.RESET} {company_number}")
                print(f"      {Fore.YELLOW}Status:{Fore.RESET} {detail.get('company_status', 'N/A')}")
                print(f"      {Fore.YELLOW}Type:{Fore.RESET} {detail.get('type', 'N/A')}")
        print()

    input(f"{Fore.YELLOW}Press Enter to return...{Fore.RESET}")
