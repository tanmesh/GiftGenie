import React from 'react';
// import GiftInput from './components/GiftInputs'
import Status from './components/Status';
import { QueryClient, QueryClientProvider } from 'react-query';

const queryClient = new QueryClient();

function Title({ name }) {
  return (
    <h1 className="text-3xl font-bold text-center">
      🎁{name}🎁
    </h1>
  )
}


function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex flex-col justify-center items-center p-4 mx-5">
        <Title name="GiftGenie" />
        {/* <GiftInput /> */}
        <Status />
      </div>
    </QueryClientProvider>
  );
}

export default App;