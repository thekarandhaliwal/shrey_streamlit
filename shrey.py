import logging
from truedata.analytics import TD_analytics
from datetime import datetime
import pandas as pd
import requests
import streamlit as st
from truedata.history import TD_hist
import time

def main():
    st.title("Values")
    
    # User input for x and y values
    x = st.number_input('Excpected Premium:', value=6000.0, format="%.2f")
    y = st.number_input('Percentage:', value=10.0, format="%.2f")

    if 'run_analysis' not in st.session_state:
        st.session_state.run_analysis = False

    if st.button('Run Analysis'):
        st.session_state.run_analysis = True

    if st.session_state.run_analysis:
        start_time = time.time()  # Start time of the analysis
        progress_bar = st.progress(0)
        counter = 0
        total_steps = 12

        try:
            my_analytics = TD_analytics(login_id='True9001', password='praviin@9001', log_level=logging.DEBUG)
            counter += 1
            progress_bar.progress(counter / total_steps)

            url = "https://api.truedata.in/getAllSymbols?segment=fo&user=True9001&password=praviin@9001&json=true&allexpiry=false&token=true&exchsymbol=NIFTY"
            response = requests.get(url)
            counter += 1
            progress_bar.progress(counter / total_steps)

            new = [i[11] for i in response.json()['Records']] if response.status_code == 200 else []
            sym = sorted(set(i for i in new if 'NIFTY' not in i))
            sym.remove("L&TFH")
            counter += 1
            progress_bar.progress(counter / total_steps)

            data = response.json()['Records']
            df1 = pd.DataFrame(data)
            df1.columns = [str(i) for i in range(23)]
            counter += 1
            progress_bar.progress(counter / total_steps)

            wow = [list(set(df1[df1['11'] == j]['5'].tolist()))[0] for j in sym]
            df = pd.DataFrame({'symbol': sym, 'LOT': wow})
            otm = float(y)
            exp = float(x)
            df = df.sort_values(by='symbol')
            counter += 1
            progress_bar.progress(counter / total_steps)

            td_hist = TD_hist('True9001', 'praviin@9001', log_level=logging.WARNING)
            a = df["symbol"].tolist()
            b, c = [], []
            for i in a:
                try:
                    res1 = td_hist.get_n_historical_bars(i, no_of_bars=2, bar_size='eod')
                    if len(res1) == 2:
                        c.append(res1.dclose.iloc[1])
                        b.append(res1.dclose.iloc[0])
                    else:
                        b.append(res1.dclose.iloc[0])
                        c.append(0)
                except:
                    b.append(0)
                    c.append(0)
            counter += 1
            progress_bar.progress(counter / total_steps)

            df['Previous'] = c    
            df["LTP"] = b
            df['%'] = round(((df['LTP'] - df['Previous']) / df['Previous']) * 100, 2)
            df['change'] = df.LTP - df.Previous
            df['call_price'] = df.LTP * (1 + otm / 100)
            df['put_price'] = df.LTP * (1 - otm / 100)
            counter += 1
            progress_bar.progress(counter / total_steps)

            def find_nearest(numbers, target):
                return min(numbers, key=lambda x: abs(x - target))

            a = [datetime.strptime(i[7], '%Y-%m-%dT%H:%M:%S') for i in response.json()['Records'] if i[11] == df.symbol.iloc[0]] if response.status_code == 200 else []
            b = sorted(set(a))
            df['expected premium']=x/df.LOT
            # callp, putp, callstrike, putstrike, excpected, new = [], [], [], [], [], []

            # for j, k, l, m, n in zip(df.symbol, df.call_price, df.put_price, df.LTP, df.LOT):
            #     try:
            #         chain = my_analytics.get_option_chain(symbol=j, expiry=b[0], greeks=True)
            #         chain['strike'] = chain['strike'].astype(float)
            #         chain['civ'] = chain['civ'].astype(float)
            #         chain['piv'] = chain['piv'].astype(float)
            #         chain['putLTP'] = chain['putLTP'].astype(float)
            #         chain['callltp'] = chain['callltp'].astype(float)
            #         nearest_call = find_nearest(chain.strike.tolist(), k)
            #         callstrike.append(nearest_call)
            #         chain1 = chain[chain.strike == nearest_call]
            #         call_premium = chain1.callltp.iloc[0]
            #         callp.append(call_premium)
            #         nearest_put = find_nearest(chain.strike.tolist(), l)
            #         putstrike.append(nearest_put)
            #         chain2 = chain[chain.strike == nearest_put]
            #         put_premium = chain2.putLTP.iloc[0]
            #         putp.append(put_premium)
            #         nearest = find_nearest(chain.strike.tolist(), m)
            #         chain3 = chain[chain.strike == nearest]
            #         new.append(round(((chain3.civ.tolist()[0] + chain3.piv.tolist()[0]) / 2) * 100, 2))
            #         excpected_premium = round(float(exp) / float(n), 2)
            #         excpected.append(excpected_premium)
            #     except:
            #         callp.append(0)
            #         putp.append(0)
            #         putstrike.append(0)
            #         new.append(0)
            #         excpected_premium = round(float(exp) / float(n), 2)
            #         excpected.append(excpected_premium)
            #         callstrike.append(0)
            #     counter += 1
            #     progress_bar.progress(min(counter / total_steps, 1.0))

            # df['call premium'] = callp
            # df['put premium'] = putp
            # df['call strike'] = callstrike
            # df['put strike'] = putstrike
            # df['excpected premium'] = excpected
            # df['IV'] = new
            # df = df.drop(columns=['call_price', "put_price"])
            # df = df[['symbol', 'LOT', 'Previous', 'LTP', '%', 'change', 'call strike', 'put strike', 'excpected premium', 'call premium', 'put premium', 'IV']]
            # df.replace([pd.NA, float('inf'), float('-inf')], 0, inplace=True)
            counter += 1
            progress_bar.progress(min(counter / total_steps, 1.0))

            st.dataframe(df)
            counter += 1
            progress_bar.progress(min(counter / total_steps, 1.0))
            current_time = datetime.now().strftime('%H:%M:%S')

# Print the current time as 11:00:00

            # Display the current time on Streamlit
            st.write("Last Updated:", current_time)

        except Exception as e:
            st.error(f"An error occurred: {e}")

        elapsed_time = time.time() - start_time
        st.text(f"Total time taken: {elapsed_time:.2f} seconds")  # Display total time taken
    
if __name__ == "_main_":
    main()
