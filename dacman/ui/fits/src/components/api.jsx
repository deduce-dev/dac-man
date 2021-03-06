import React, { useState, useEffect } from 'react';
import { useForm } from "react-hooks-helper";


export function useBackendData(endpoint, params = {}) {
  const [status, setStatus] = useState({});
  const [data, setData] = useState();
  const url = `/datadiff${endpoint}`;
  const paramsStr = JSON.stringify(params);

  const req = new Request(
    url,
    {
      ...params
    }
  );

  useEffect( () => {
      const fetchData = async () => {
        setStatus('fetching');
        const resp = await fetch(req);
        const respData =  await resp.json();
        setData(respData);
        setStatus({...status, OK: true});
      };
      fetchData();
  }, [url, paramsStr]); 
  
  const Loading = () => {
    return (
      <h1>Loading...</h1>
    )
  };

  return {status, data, Loading};
}


export function useBackendDispatch(endpoint, payload = {}) {
  const [status, setStatus] = useState({});
  const [data, setData] = useState();
  const url = `/datadiff${endpoint}`;
  const payloadJSON = JSON.stringify(payload);

  const req = new Request(
    url,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: payloadJSON
    }
  );

  useEffect( () => {
      const dispatchRequest = async () => {
        setStatus('fetching');
        const resp = await fetch(req);
        const respData =  await resp.json();
        setData(respData);
        setStatus({...status, OK: true});
      };
      dispatchRequest();
  }, [url, payloadJSON]); 

  return {status, data};
}


export function useBuildData() {
  const INITIAL = {
    base: "",
    new: "",
    sample_file: "",
    fields: [],
  };

  const [data, setData] = useForm(INITIAL);
  return [data, setData];
}
