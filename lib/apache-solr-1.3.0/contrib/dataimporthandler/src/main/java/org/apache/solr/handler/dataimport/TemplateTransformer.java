/**
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.solr.handler.dataimport;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

/**
 * <p>
 * A Transformer which can put values into a column by resolving an expression
 * containing other columns
 * </p>
 * <p/>
 * <p>
 * For example:<br />
 * &lt;field column="name" template="${e.lastName}, ${e.firstName}
 * ${e.middleName}" /&gt; will produce the name by combining values from
 * lastName, firstName and middleName fields as given in the template attribute.
 * </p>
 * <p/>
 * <p>
 * Refer to <a
 * href="http://wiki.apache.org/solr/DataImportHandler">http://wiki.apache.org/solr/DataImportHandler</a>
 * for more details.
 * </p>
 * <p/>
 * <b>This API is experimental and may change in the future.</b>
 *
 * @version $Id: TemplateTransformer.java 681182 2008-07-30 19:35:58Z shalin $
 * @since solr 1.3
 */
public class TemplateTransformer extends Transformer {

  private static final Logger LOG = Logger.getLogger(TemplateTransformer.class
          .getName());

  @SuppressWarnings("unchecked")
  public Object transformRow(Map<String, Object> row, Context context) {

    String entityName = context.getEntityAttribute(DataImporter.NAME);

    VariableResolverImpl resolver = (VariableResolverImpl) context
            .getVariableResolver();
    Map<String, Object> resolverMap = (Map<String, Object>) resolver
            .resolve(entityName);

    // Clone resolver map because the resolver map contains common fields or any
    // others
    // that the entity processor chooses to keep.
    Map<String, Object> resolverMapCopy = new HashMap<String, Object>();
    if (resolverMap != null) {
      for (Map.Entry<String, Object> entry : resolverMap.entrySet())
        resolverMapCopy.put(entry.getKey(), entry.getValue());
    }
    // Add current row to the copy of resolver map
    for (Map.Entry<String, Object> entry : row.entrySet())
      resolverMapCopy.put(entry.getKey(), entry.getValue());
    // Add this copy to the namespace of the current entity in the resolver
    resolver.addNamespace(entityName, resolverMapCopy);

    for (Map<String, String> map : context.getAllEntityFields()) {
      String expr = map.get(TEMPLATE);
      if (expr == null)
        continue;

      String column = map.get(DataImporter.COLUMN);

      // Verify if all variables can be resolved or not
      boolean resolvable = true;
      List<String> variables = TemplateString.getVariables(expr);
      for (String v : variables) {
        if (resolver.resolve(v) == null) {
          LOG.warning("Unable to resolve variable: " + v
                  + " while parsing expression: " + expr);
          resolvable = false;
        }
      }

      if (!resolvable)
        continue;

      row.put(column, resolver.replaceTokens(expr));
    }

    // Restore the original resolver map
    resolver.addNamespace(entityName, resolverMap);

    return row;
  }

  public static final String TEMPLATE = "template";
}
