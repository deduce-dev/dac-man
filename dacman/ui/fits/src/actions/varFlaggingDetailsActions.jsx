

export basicCheckboxChange = (event) => {
  return {
    type: 'CHECKBOX_CHANGE',
    payload: {
      name: event.target.name,
      checked: event.target.checked
    }
  };
};

export duplicatesCheckboxChange = (event) => {
  return {
    type: 'DUPLICATES_CHECKBOX_CHANGE',
    payload: event.target.checked
  };
};

export subsequentCheckboxChange = (event) => {
  return {
    type: 'SUBSEQUENT_CHECKBOX_CHANGE',
    payload: event.target.checked
  };
};

export subsequentNumChange = (event) => {
  return{
    type: 'SUBSEQUENT_NUM_CHANGE',
    payload: event.target.value
  };
};
