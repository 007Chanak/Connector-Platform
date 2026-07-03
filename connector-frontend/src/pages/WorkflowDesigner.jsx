import { useState } from "react";
import api from "../services/api";

function WorkflowDesigner() {

  const [entity, setEntity] =
    useState("customers");

  const [editableMappings, setEditableMappings] =
    useState(null);

  const [disabledMappings, setDisabledMappings] =
    useState({
      source: {},
      target: {}
    });

  const getToken = () => {
    return localStorage.getItem("token");
  };

  const previewMapping = async () => {

    try {

      const response = await api.post(
        `/mapping/preview/${entity}`,
        {},
        {
          headers: {
            Authorization:
              `Bearer ${getToken()}`
          }
        }
      );

      setEditableMappings(
        JSON.parse(
          JSON.stringify(
            response.data
          )
        )
      );

      setDisabledMappings({
        source: {},
        target: {}
      });

    } catch (error) {

      console.error(error);

      alert(
        "Failed to load mapping"
      );
    }
  };

  const updateSourceMapping = (
    sourceField,
    value
  ) => {

    const updated =
      JSON.parse(
        JSON.stringify(
          editableMappings
        )
      );

    updated.source_to_unified[
      sourceField
    ] = value;

    setEditableMappings(
      updated
    );
  };

  const toggleSourceMapping = (
    sourceField
  ) => {

    setDisabledMappings(
      prev => ({

        ...prev,

        source: {

          ...prev.source,

          [sourceField]:
            !prev.source[
              sourceField
            ]
        }
      })
    );
  };

  const updateTargetMapping = (
    doctype,
    unifiedField,
    value
  ) => {

    const updated =
      JSON.parse(
        JSON.stringify(
          editableMappings
        )
      );

    if (
      !updated
        .unified_to_target[
          doctype
        ]
        .mapping[
          unifiedField
        ]
    ) {

      updated
        .unified_to_target[
          doctype
        ]
        .mapping[
          unifiedField
        ] = value;

    } else {

      updated
        .unified_to_target[
          doctype
        ]
        .mapping[
          unifiedField
        ] = value;
    }

    setEditableMappings(
      updated
    );
  };

  const toggleTargetMapping = (
    doctype,
    unifiedField
  ) => {

    const key =
      `${doctype}:${unifiedField}`;

    setDisabledMappings(
      prev => ({

        ...prev,

        target: {

          ...prev.target,

          [key]:
            !prev.target[
              key
            ]
        }
      })
    );
  };

  const getUnmappedFields = (
    doctype,
    config
  ) => {

    const mappedFields =
      Object.keys(
        config.mapping
      );

    const allowedFields =
      editableMappings
        .unified_field_groups[
          doctype
        ] || [];

    return allowedFields.filter(
      field =>
        !mappedFields.includes(
          field
        )
    );
  };

  const saveMapping = async () => {

    console.log(
      "SAVE PAYLOAD",
      {
        mappings:
          editableMappings,

        disabled:
          disabledMappings
      }
    );

    try {

      await api.post(

        `/workflow/save/${entity}`,

        {

          mappings:
            editableMappings,

          disabled:
            disabledMappings

        },

        {

          headers: {

            Authorization:
              `Bearer ${getToken()}`
          }
        }
      );

      alert(
        "Workflow saved successfully"
      );

    } catch (error) {

      console.error(
        error
      );

      alert(
        "Failed to save workflow"
      );
    }
  };

  return (

    <div>

      <h1 className="text-4xl font-bold mb-6">
        Workflow Designer
      </h1>

      <div className="mb-6">

        <label className="block font-semibold mb-2">
          Entity
        </label>

        <select

          value={entity}

          onChange={(e) =>
            setEntity(
              e.target.value
            )
          }

          className="
            border
            rounded
            p-2
            w-64
          "
        >

          <option value="customers">
            Customers
          </option>

          <option value="suppliers">
            Suppliers
          </option>

          <option value="items">
            Items
          </option>

          <option value="bills">
            Bills
          </option>

          <option value="invoices">
            Invoices
          </option>

          <option value="purchase-orders">
            Purchase Orders
          </option>

          <option value="sales-orders">
            Sales Orders
          </option>

        </select>

      </div>

      <button

        onClick={previewMapping}

        className="
          bg-blue-600
          text-white
          px-4
          py-2
          rounded
          mb-6
        "
      >

        Preview Mapping

      </button>

      {editableMappings && (

        <div>

          <h2 className="text-2xl font-bold mb-4">
            Xero → Unified
          </h2>

          <table className="w-full border bg-white mb-8">

            <thead>

              <tr className="bg-gray-200">

                <th className="border p-2">
                  Source Field
                </th>

                <th className="border p-2">
                  Unified Field
                </th>

                <th className="border p-2">
                  Action
                </th>

              </tr>

            </thead>

            <tbody>

              {Object.entries(
                editableMappings
                  .source_to_unified
              ).map(
                ([source, unified]) => (

                  <tr
                    key={source}
                    className={
                      disabledMappings
                        .source[
                          source
                        ]
                        ? "opacity-40 bg-gray-100"
                        : ""
                    }
                  >

                    <td className="border p-2">
                      {source}
                    </td>

                    <td className="border p-2">

                      <select

                        value={unified}

                        onChange={(e) =>
                          updateSourceMapping(
                            source,
                            e.target.value
                          )
                        }

                        className="
                          border
                          rounded
                          p-1
                          w-full
                        "
                      >

                        {editableMappings
                          .available_unified_fields
                          .map(
                            (field) => (

                              <option
                                key={field}
                                value={field}
                              >
                                {field}
                              </option>

                            )
                          )}

                      </select>

                    </td>

                    <td className="border p-2">

                      <button

                        onClick={() =>
                          toggleSourceMapping(
                            source
                          )
                        }

                        className={
                          disabledMappings
                            .source[
                              source
                            ]

                            ? "bg-green-600 text-white px-3 py-1 rounded"

                            : "bg-red-600 text-white px-3 py-1 rounded"
                        }

                      >

                        {
                          disabledMappings
                            .source[
                              source
                            ]

                            ? "Restore"

                            : "Disable"
                        }

                      </button>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

          <h2 className="text-2xl font-bold mb-4">
            Unified → ERPNext
          </h2>

          {Object.entries(
            editableMappings
              .unified_to_target
          ).map(
            ([doctype, config]) => (

              <div
                key={doctype}
                className="mb-8"
              >

                <h3 className="text-xl font-bold mb-3">
                  {doctype}
                </h3>

                <table className="w-full border bg-white">

                  <thead>

                    <tr className="bg-gray-200">

                      <th className="border p-2">
                        Unified Field
                      </th>

                      <th className="border p-2">
                        ERPNext Field
                      </th>

                      <th className="border p-2">
                        Action
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {Object.entries(
                      config.mapping
                    ).map(
                      ([unified, target]) => (

                        <tr
                          key={`${doctype}-${unified}`}
                          className={
                            disabledMappings.target[
                              `${doctype}:${unified}`
                            ]
                              ? "opacity-40 bg-gray-100"
                              : ""
                          }
                        >

                          <td className="border p-2">
                            {unified}
                          </td>

                          <td className="border p-2">

                            <select

                              value={target}

                              onChange={(e) =>
                                updateTargetMapping(
                                  doctype,
                                  unified,
                                  e.target.value
                                )
                              }

                              className="
                                border
                                rounded
                                p-1
                                w-full
                              "
                            >

                              {config.available_fields.map(
                                (field) => (

                                  <option
                                    key={field}
                                    value={field}
                                  >
                                    {field}
                                  </option>

                                )
                              )}

                            </select>

                          </td>

                          <td className="border p-2">

                            <button

                              onClick={() =>
                                toggleTargetMapping(
                                  doctype,
                                  unified
                                )
                              }

                              className={
                                disabledMappings.target[
                                  `${doctype}:${unified}`
                                ]

                                  ? "bg-green-600 text-white px-3 py-1 rounded"

                                  : "bg-red-600 text-white px-3 py-1 rounded"
                              }

                            >

                              {
                                disabledMappings.target[
                                  `${doctype}:${unified}`
                                ]

                                  ? "Restore"

                                  : "Disable"
                              }

                            </button>

                          </td>

                        </tr>

                      )
                    )}

                    {getUnmappedFields(
                      doctype,
                      config
                    ).map(
                      (unified) => (

                        <tr
                          key={`${doctype}-new-${unified}`}
                        >

                          <td className="border p-2">
                            {unified}
                          </td>

                          <td className="border p-2">

                            <select

                              defaultValue=""

                              onChange={(e) =>
                                updateTargetMapping(
                                  doctype,
                                  unified,
                                  e.target.value
                                )
                              }

                              className="
                                border
                                rounded
                                p-1
                                w-full
                              "
                            >

                              <option value="">
                                Select ERPNext Field
                              </option>

                              {config.available_fields.map(
                                (field) => (

                                  <option
                                    key={field}
                                    value={field}
                                  >
                                    {field}
                                  </option>

                                )
                              )}

                            </select>

                          </td>

                          <td className="border p-2">
                            New Mapping
                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            )
          )}

          <button

            onClick={saveMapping}

            className="
              bg-green-600
              text-white
              px-6
              py-3
              rounded
            "

          >
            Save Mapping
          </button>

        </div>

      )}

    </div>
  );
}

export default WorkflowDesigner;