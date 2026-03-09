"""MCP tools for the Aladdin Security Creation API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_SECURITY_CREATION_BASE_PATH = "/api/data/reference-data/asset/asset-creation/v1/"

_client: AladdinRestClient | None = None


def _get_client() -> AladdinRestClient:
    global _client
    if _client is None:
        _client = AladdinRestClient(
            default_web_server=server_config.default_web_server,
            oauth_config=server_config.oauth,
            lro_config=server_config.lro,
            pagination_config=server_config.pagination,
        )
    return _client


def _call_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Security Creation API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_SECURITY_CREATION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Security Creation API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_security_creation_tools(mcp: FastMCP) -> None:
    """Register Aladdin Security Creation API tools with the MCP server."""

    @mcp.tool()
    def create_arm_tba_security(
        agency: str,
        term: int,
        initial_coupon: float,
        wac: float,
        wam: int,
        wala: int,
        months_to_roll: int | None = None,
        gross_margin: float | None = None,
        net_margin: float | None = None,
        cap_structure: str | None = None,
        index: str | None = None,
        arm_structure: str | None = None,
        look_back_day_count: int | None = None,
        negative_amortization_cap: float | None = None,
        convertible: bool | None = None,
    ) -> str:
        """Create an ARM/TBA security.

        Required fields for ARM/TBA creation are agency, term, initialCoupon,
        wac, wam, and wala.

        Args:
            agency: Agency code (e.g. GNMAII).
            term: Term in years (e.g. 10).
            initial_coupon: Initial coupon rate (e.g. 1.0).
            wac: Weighted average coupon (e.g. 20.0).
            wam: Weighted average maturity in months (e.g. 56).
            wala: Weighted average loan age in months (e.g. 100).
            months_to_roll: Number of months to roll.
            gross_margin: Gross margin value.
            net_margin: Net margin value.
            cap_structure: Cap structure descriptor.
            index: Index reference.
            arm_structure: ARM structure descriptor.
            look_back_day_count: Look-back day count.
            negative_amortization_cap: Negative amortization cap.
            convertible: Whether the security is convertible.
        """
        body: dict[str, Any] = {
            "tbaInfo": {"agency": agency, "term": term},
            "initialCoupon": initial_coupon,
            "wac": wac,
            "wam": wam,
            "wala": wala,
        }
        if months_to_roll is not None:
            body["monthsToRoll"] = months_to_roll
        if gross_margin is not None:
            body["grossMargin"] = gross_margin
        if net_margin is not None:
            body["netMargin"] = net_margin
        if cap_structure is not None:
            body["capStructure"] = cap_structure
        if index is not None:
            body["index"] = index
        if arm_structure is not None:
            body["armStructure"] = arm_structure
        if look_back_day_count is not None:
            body["lookBackDayCount"] = look_back_day_count
        if negative_amortization_cap is not None:
            body["negativeAmortizationCap"] = negative_amortization_cap
        if convertible is not None:
            body["convertible"] = convertible

        return _call_api("/armTbaSecurity", request_body=body)

    @mcp.tool()
    def create_cash_repo_security(
        currency_code: str,
        maturity_date: str,
        rate: float,
        accrual_base: str | None = None,
        accrual_date: str | None = None,
        collateral_type: str | None = None,
        fee: float | None = None,
        callable: bool | None = None,
        call_delay_day_count: int | None = None,
        variable_rate: bool | None = None,
        spread: float | None = None,
        lookback_calendar_codes: list[str] | None = None,
        lookback_type: str | None = None,
        look_back_day_count: int | None = None,
        lockout_day_count: int | None = None,
    ) -> str:
        """Create a CASH/REPO security.

        Args:
            currency_code: Currency code (e.g. USD).
            maturity_date: Maturity date (YYYY-MM-DD).
            rate: Interest rate.
            accrual_base: Accrual base type.
            accrual_date: Accrual start date (YYYY-MM-DD).
            collateral_type: Collateral type descriptor.
            fee: Fee amount.
            callable: Whether the security is callable.
            call_delay_day_count: Call delay day count.
            variable_rate: Whether the rate is variable.
            spread: Spread value.
            lookback_calendar_codes: List of lookback calendar codes.
            lookback_type: Lookback type.
            look_back_day_count: Look-back day count.
            lockout_day_count: Lockout day count.
        """
        body: dict[str, Any] = {
            "currencyCode": currency_code,
            "maturityDate": maturity_date,
            "rate": rate,
        }
        if accrual_base is not None:
            body["accrualBase"] = accrual_base
        if accrual_date is not None:
            body["accrualDate"] = accrual_date
        if collateral_type is not None:
            body["collateralType"] = collateral_type
        if fee is not None:
            body["fee"] = fee
        if callable is not None:
            body["callable"] = callable
        if call_delay_day_count is not None:
            body["callDelayDayCount"] = call_delay_day_count
        if variable_rate is not None:
            body["variableRate"] = variable_rate
        if spread is not None:
            body["spread"] = spread
        if lookback_calendar_codes is not None:
            body["lookbackCalendarCodes"] = lookback_calendar_codes
        if lookback_type is not None:
            body["lookbackType"] = lookback_type
        if look_back_day_count is not None:
            body["lookBackDayCount"] = look_back_day_count
        if lockout_day_count is not None:
            body["lockoutDayCount"] = lockout_day_count

        return _call_api("/cashRepoSecurity", request_body=body)

    @mcp.tool()
    def create_cash_time_deposit_security(
        currency_code: str,
        maturity_date: str,
        rate: float,
        country_code: str | None = None,
        market_country_code: str | None = None,
        accrual_base: str | None = None,
        accrual_date: str | None = None,
        first_coupon_date: str | None = None,
        rate_type: str | None = None,
        initial_rate: float | None = None,
        payment_frequency_type: str | None = None,
        payment_calendar_codes: list[str] | None = None,
        security_description: str | None = None,
        registration: str | None = None,
        registration_right: str | None = None,
    ) -> str:
        """Create a CASH/TD (time deposit) security.

        Args:
            currency_code: Currency code (e.g. USD).
            maturity_date: Maturity date (YYYY-MM-DD).
            rate: Interest rate.
            country_code: Country code.
            market_country_code: Market country code.
            accrual_base: Accrual base type.
            accrual_date: Accrual start date (YYYY-MM-DD).
            first_coupon_date: First coupon date (YYYY-MM-DD).
            rate_type: Rate type descriptor.
            initial_rate: Initial rate value.
            payment_frequency_type: Payment frequency type.
            payment_calendar_codes: List of payment calendar codes.
            security_description: Description of the security.
            registration: Registration information.
            registration_right: Registration right information.
        """
        body: dict[str, Any] = {
            "currencyCode": currency_code,
            "maturityDate": maturity_date,
            "rate": rate,
        }
        if country_code is not None:
            body["countryCode"] = country_code
        if market_country_code is not None:
            body["marketCountryCode"] = market_country_code
        if accrual_base is not None:
            body["accrualBase"] = accrual_base
        if accrual_date is not None:
            body["accrualDate"] = accrual_date
        if first_coupon_date is not None:
            body["firstCouponDate"] = first_coupon_date
        if rate_type is not None:
            body["rateType"] = rate_type
        if initial_rate is not None:
            body["initialRate"] = initial_rate
        if payment_frequency_type is not None:
            body["paymentFrequencyType"] = payment_frequency_type
        if payment_calendar_codes is not None:
            body["paymentCalendarCodes"] = payment_calendar_codes
        if security_description is not None:
            body["securityDescription"] = security_description
        if registration is not None:
            body["registration"] = registration
        if registration_right is not None:
            body["registrationRight"] = registration_right

        return _call_api("/cashTimeDepositSecurity", request_body=body)

    @mcp.tool()
    def create_cds_security(
        reference_entity: str,
        currency_code: str,
        start_date: str,
        maturity_date: str,
        deal_spread: float,
        reference_security_id: str | None = None,
        red_code: str | None = None,
        restructure_type: str | None = None,
        seniority: str | None = None,
        exchange: str | None = None,
        counterparty: str | None = None,
    ) -> str:
        """Create a CDS (Credit Default Swap) security.

        Args:
            reference_entity: Reference entity name.
            currency_code: Currency code (e.g. USD).
            start_date: Start date (YYYY-MM-DD).
            maturity_date: Maturity date (YYYY-MM-DD).
            deal_spread: Deal spread in basis points.
            reference_security_id: Reference security identifier.
            red_code: RED code.
            restructure_type: Restructure type.
            seniority: Seniority level.
            exchange: Exchange code.
            counterparty: Counterparty identifier.
        """
        body: dict[str, Any] = {
            "referenceEntity": reference_entity,
            "currencyCode": currency_code,
            "startDate": start_date,
            "maturityDate": maturity_date,
            "dealSpread": deal_spread,
        }
        if reference_security_id is not None:
            body["referenceSecurityId"] = reference_security_id
        if red_code is not None:
            body["redCode"] = red_code
        if restructure_type is not None:
            body["restructureType"] = restructure_type
        if seniority is not None:
            body["seniority"] = seniority
        if exchange is not None:
            body["exchange"] = exchange
        if counterparty is not None:
            body["counterparty"] = counterparty

        return _call_api("/cdsSecurity", request_body=body)

    @mcp.tool()
    def create_cdx_security(
        cdx_info: dict[str, Any],
        exchange: str | None = None,
        counterparty: str | None = None,
    ) -> str:
        """Create a CDX (Credit Default Swap Index) security.

        Args:
            cdx_info: CDX information dict containing index details.
            exchange: Exchange code.
            counterparty: Counterparty identifier.
        """
        body: dict[str, Any] = {"cdxInfo": cdx_info}
        if exchange is not None:
            body["exchange"] = exchange
        if counterparty is not None:
            body["counterparty"] = counterparty

        return _call_api("/cdxSecurity", request_body=body)

    @mcp.tool()
    def create_equity_equity_security(
        ticker: str,
        name: str,
        currency_code: str,
        country_code: str,
        exchange: str,
        registration_flag: bool | None = None,
        lot_size: int | None = None,
        asset_id: str | None = None,
        sedol: str | None = None,
        offering_info: dict[str, Any] | None = None,
        counterparty: str | None = None,
    ) -> str:
        """Create an EQUITY/EQUITY security.

        Args:
            ticker: Ticker symbol.
            name: Security name.
            currency_code: Currency code (e.g. USD).
            country_code: Country code (e.g. US).
            exchange: Exchange code.
            registration_flag: Whether registration flag is set.
            lot_size: Lot size for the security.
            asset_id: Aladdin asset ID.
            sedol: SEDOL identifier.
            offering_info: Offering information dict.
            counterparty: Counterparty identifier.
        """
        body: dict[str, Any] = {
            "ticker": ticker,
            "name": name,
            "currencyCode": currency_code,
            "countryCode": country_code,
            "exchange": exchange,
        }
        if registration_flag is not None:
            body["registrationFlag"] = registration_flag
        if lot_size is not None:
            body["lotSize"] = lot_size
        if asset_id is not None:
            body["assetId"] = asset_id
        if sedol is not None:
            body["sedol"] = sedol
        if offering_info is not None:
            body["offeringInfo"] = offering_info
        if counterparty is not None:
            body["counterparty"] = counterparty

        return _call_api("/equityEquitySecurity", request_body=body)

    @mcp.tool()
    def create_equity_option_security(
        equity_option_type: str,
        underlying_asset_id: str,
        currency_code: str,
        call_put_type: str,
        expiration_date: str,
        strike_price: float,
        underlying_exchange: str | None = None,
        notional_amount: float | None = None,
        settlement_method: str | None = None,
        option_style: str | None = None,
        option_ticker: str | None = None,
        fx_rate: float | None = None,
        expiry_time: str | None = None,
        barrier_event: str | None = None,
        lower_barrier: float | None = None,
    ) -> str:
        """Create an Equity Option security.

        Args:
            equity_option_type: Type of equity option.
            underlying_asset_id: Underlying asset identifier.
            currency_code: Currency code (e.g. USD).
            call_put_type: CALL or PUT.
            expiration_date: Expiration date (YYYY-MM-DD).
            strike_price: Strike price.
            underlying_exchange: Underlying exchange code.
            notional_amount: Notional amount.
            settlement_method: Settlement method.
            option_style: Option style (e.g. AMERICAN, EUROPEAN).
            option_ticker: Option ticker symbol.
            fx_rate: FX rate.
            expiry_time: Expiry time.
            barrier_event: Barrier event type.
            lower_barrier: Lower barrier level.
        """
        body: dict[str, Any] = {
            "equityOptionType": equity_option_type,
            "underlyingAssetId": underlying_asset_id,
            "currencyCode": currency_code,
            "callPutType": call_put_type,
            "expirationDate": expiration_date,
            "strikePrice": strike_price,
        }
        if underlying_exchange is not None:
            body["underlyingExchange"] = underlying_exchange
        if notional_amount is not None:
            body["notionalAmount"] = notional_amount
        if settlement_method is not None:
            body["settlementMethod"] = settlement_method
        if option_style is not None:
            body["optionStyle"] = option_style
        if option_ticker is not None:
            body["optionTicker"] = option_ticker
        if fx_rate is not None:
            body["fxRate"] = fx_rate
        if expiry_time is not None:
            body["expiryTime"] = expiry_time
        if barrier_event is not None:
            body["barrierEvent"] = barrier_event
        if lower_barrier is not None:
            body["lowerBarrier"] = lower_barrier

        return _call_api("/equityOptionSecurity", request_body=body)

    @mcp.tool()
    def create_futures_security(
        ric: str,
        contract_name: str,
        contract_year: int,
        contract_month: int,
        strike: float | None = None,
        call_put_type: str | None = None,
    ) -> str:
        """Create a Futures security.

        Args:
            ric: Reuters Instrument Code.
            contract_name: Contract name.
            contract_year: Contract year.
            contract_month: Contract month (1-12).
            strike: Strike price (for futures options).
            call_put_type: CALL or PUT (for futures options).
        """
        body: dict[str, Any] = {
            "ric": ric,
            "contractName": contract_name,
            "contractYear": contract_year,
            "contractMonth": contract_month,
        }
        if strike is not None:
            body["strike"] = strike
        if call_put_type is not None:
            body["callPutType"] = call_put_type

        return _call_api("/futuresSecurity", request_body=body)

    @mcp.tool()
    def create_fx_option_security(
        currency_pair: str,
        expiration_date: str,
        delivery_date: str,
        call_put_type: str,
        strike: float,
        option_style: str | None = None,
        expiry_time: str | None = None,
        non_deliverable: bool | None = None,
        fx_rate_reference: str | None = None,
        lower_barrier: float | None = None,
        upper_barrier: float | None = None,
        barrier_start_date: str | None = None,
        barrier_end_date: str | None = None,
        barrier_source: str | None = None,
        settlement_currency: str | None = None,
    ) -> str:
        """Create an FX Option security.

        Args:
            currency_pair: Currency pair (e.g. EURUSD).
            expiration_date: Expiration date (YYYY-MM-DD).
            delivery_date: Delivery date (YYYY-MM-DD).
            call_put_type: CALL or PUT.
            strike: Strike price.
            option_style: Option style (e.g. AMERICAN, EUROPEAN).
            expiry_time: Expiry time.
            non_deliverable: Whether the option is non-deliverable.
            fx_rate_reference: FX rate reference.
            lower_barrier: Lower barrier level.
            upper_barrier: Upper barrier level.
            barrier_start_date: Barrier start date (YYYY-MM-DD).
            barrier_end_date: Barrier end date (YYYY-MM-DD).
            barrier_source: Barrier source.
            settlement_currency: Settlement currency code.
        """
        body: dict[str, Any] = {
            "currencyPair": currency_pair,
            "expirationDate": expiration_date,
            "deliveryDate": delivery_date,
            "callPutType": call_put_type,
            "strike": strike,
        }
        if option_style is not None:
            body["optionStyle"] = option_style
        if expiry_time is not None:
            body["expiryTime"] = expiry_time
        if non_deliverable is not None:
            body["nonDeliverable"] = non_deliverable
        if fx_rate_reference is not None:
            body["fxRateReference"] = fx_rate_reference
        if lower_barrier is not None:
            body["lowerBarrier"] = lower_barrier
        if upper_barrier is not None:
            body["upperBarrier"] = upper_barrier
        if barrier_start_date is not None:
            body["barrierStartDate"] = barrier_start_date
        if barrier_end_date is not None:
            body["barrierEndDate"] = barrier_end_date
        if barrier_source is not None:
            body["barrierSource"] = barrier_source
        if settlement_currency is not None:
            body["settlementCurrency"] = settlement_currency

        return _call_api("/fxOptionSecurity", request_body=body)

    @mcp.tool()
    def create_fx_security(
        currency_pair: str,
        value_date: str,
        rate: float,
        fx_type: str,
    ) -> str:
        """Create an FX SPOT, FX FWRD, or FX CSWAP security.

        Args:
            currency_pair: Currency pair (e.g. EURUSD).
            value_date: Value date (YYYY-MM-DD).
            rate: FX rate.
            fx_type: FX type (e.g. SPOT, FWRD, CSWAP).
        """
        body: dict[str, Any] = {
            "currencyPair": currency_pair,
            "valueDate": value_date,
            "rate": rate,
            "fxType": fx_type,
        }
        return _call_api("/fxSecurity", request_body=body)

    @mcp.tool()
    def create_fxndf_security(
        currency_pair: str,
        value_date: str,
        fixing_date: str,
        exchange: str | None = None,
        fx_rate_reference: str | None = None,
        settle_location: str | None = None,
        settlement_currency_code: str | None = None,
    ) -> str:
        """Create an FX NDF (Non-Deliverable Forward) security.

        Args:
            currency_pair: Currency pair (e.g. EURUSD).
            value_date: Value date (YYYY-MM-DD).
            fixing_date: Fixing date (YYYY-MM-DD).
            exchange: Exchange code.
            fx_rate_reference: FX rate reference.
            settle_location: Settlement location.
            settlement_currency_code: Settlement currency code.
        """
        body: dict[str, Any] = {
            "currencyPair": currency_pair,
            "valueDate": value_date,
            "fixingDate": fixing_date,
        }
        if exchange is not None:
            body["exchange"] = exchange
        if fx_rate_reference is not None:
            body["fxRateReference"] = fx_rate_reference
        if settle_location is not None:
            body["settleLocation"] = settle_location
        if settlement_currency_code is not None:
            body["settlementCurrencyCode"] = settlement_currency_code

        return _call_api("/fxndfSecurity", request_body=body)

    @mcp.tool()
    def create_interest_rate_swap_security(
        swap_info: dict[str, Any],
        start_date: str,
        maturity_date: str,
        exchange: str | None = None,
        counterparty: str | None = None,
    ) -> str:
        """Create an Interest Rate Swap security.

        Args:
            swap_info: Swap information dict containing leg details.
            start_date: Start date (YYYY-MM-DD).
            maturity_date: Maturity date (YYYY-MM-DD).
            exchange: Exchange code.
            counterparty: Counterparty identifier.
        """
        body: dict[str, Any] = {
            "swapInfo": swap_info,
            "startDate": start_date,
            "maturityDate": maturity_date,
        }
        if exchange is not None:
            body["exchange"] = exchange
        if counterparty is not None:
            body["counterparty"] = counterparty

        return _call_api("/interestRateSwapSecurity", request_body=body)

    @mcp.tool()
    def create_mbs_tba_security(
        tba_info: dict[str, Any],
        coupon: float,
        pool_story: str | None = None,
    ) -> str:
        """Create an MBS/TBA (Mortgage-Backed Security To-Be-Announced) security.

        Args:
            tba_info: TBA information dict containing agency, term, etc.
            coupon: Coupon rate.
            pool_story: Pool story descriptor.
        """
        body: dict[str, Any] = {
            "tbaInfo": tba_info,
            "coupon": coupon,
        }
        if pool_story is not None:
            body["poolStory"] = pool_story

        return _call_api("/mbsTbaSecurity", request_body=body)

    @mcp.tool()
    def create_swaption_security(
        swaption_type: str,
        currency_code: str,
        call_put_type: str,
        expiration_date: str,
        strike_price: float,
        option_style: str | None = None,
        final_settlement_method: str | None = None,
        premium_in_percent: float | None = None,
        premium_date: str | None = None,
        clearing_party: str | None = None,
        underlying_term: str | None = None,
        underlying_start: str | None = None,
        underlying_clearing_party: str | None = None,
        underlying_cdx_info: dict[str, Any] | None = None,
        agreed_discount_rate: float | None = None,
    ) -> str:
        """Create a Swaption security.

        Args:
            swaption_type: Swaption type.
            currency_code: Currency code (e.g. USD).
            call_put_type: CALL or PUT.
            expiration_date: Expiration date (YYYY-MM-DD).
            strike_price: Strike price.
            option_style: Option style (e.g. AMERICAN, EUROPEAN).
            final_settlement_method: Final settlement method.
            premium_in_percent: Premium in percent.
            premium_date: Premium date (YYYY-MM-DD).
            clearing_party: Clearing party identifier.
            underlying_term: Underlying term.
            underlying_start: Underlying start date (YYYY-MM-DD).
            underlying_clearing_party: Underlying clearing party identifier.
            underlying_cdx_info: Underlying CDX information dict.
            agreed_discount_rate: Agreed discount rate.
        """
        body: dict[str, Any] = {
            "swaptionType": swaption_type,
            "currencyCode": currency_code,
            "callPutType": call_put_type,
            "expirationDate": expiration_date,
            "strikePrice": strike_price,
        }
        if option_style is not None:
            body["optionStyle"] = option_style
        if final_settlement_method is not None:
            body["finalSettlementMethod"] = final_settlement_method
        if premium_in_percent is not None:
            body["premiumInPercent"] = premium_in_percent
        if premium_date is not None:
            body["premiumDate"] = premium_date
        if clearing_party is not None:
            body["clearingParty"] = clearing_party
        if underlying_term is not None:
            body["underlyingTerm"] = underlying_term
        if underlying_start is not None:
            body["underlyingStart"] = underlying_start
        if underlying_clearing_party is not None:
            body["underlyingClearingParty"] = underlying_clearing_party
        if underlying_cdx_info is not None:
            body["underlyingCdxInfo"] = underlying_cdx_info
        if agreed_discount_rate is not None:
            body["agreedDiscountRate"] = agreed_discount_rate

        return _call_api("/swaptionSecurity", request_body=body)

    @mcp.tool()
    def create_total_return_swap_security(
        swap_info: dict[str, Any],
        rec_leg_income_fee: float | None = None,
        rec_leg_custom_schedules: list[dict[str, Any]] | None = None,
        pay_leg_custom_schedules: list[dict[str, Any]] | None = None,
        counterparty: str | None = None,
    ) -> str:
        """Create a Total Return Swap security.

        Args:
            swap_info: Swap information dict containing leg details.
            rec_leg_income_fee: Receive leg income fee.
            rec_leg_custom_schedules: Receive leg custom schedules.
            pay_leg_custom_schedules: Pay leg custom schedules.
            counterparty: Counterparty identifier.
        """
        body: dict[str, Any] = {"swapInfo": swap_info}
        if rec_leg_income_fee is not None:
            body["recLegIncomeFee"] = rec_leg_income_fee
        if rec_leg_custom_schedules is not None:
            body["recLegCustomSchedules"] = rec_leg_custom_schedules
        if pay_leg_custom_schedules is not None:
            body["payLegCustomSchedules"] = pay_leg_custom_schedules
        if counterparty is not None:
            body["counterparty"] = counterparty

        return _call_api("/totalReturnSwapSecurity", request_body=body)
