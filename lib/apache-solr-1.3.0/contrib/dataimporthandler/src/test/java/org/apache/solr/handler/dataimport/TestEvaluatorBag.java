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

import static org.junit.Assert.assertEquals;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import java.net.URLEncoder;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * <p>
 * Test for EvaluatorBag
 * </p>
 *
 * @version $Id: TestEvaluatorBag.java 681182 2008-07-30 19:35:58Z shalin $
 * @since solr 1.3
 */
public class TestEvaluatorBag {
  private static final String ENCODING = "UTF-8";

  VariableResolverImpl resolver;

  Map<String, String> sqlTests;

  Map<String, String> urlTests;

  @Before
  public void setUp() throws Exception {
    resolver = new VariableResolverImpl();

    sqlTests = new HashMap<String, String>();

    sqlTests.put("foo\"", "foo\"\"");
    sqlTests.put("foo'", "foo''");
    sqlTests.put("foo''", "foo''''");
    sqlTests.put("'foo\"", "''foo\"\"");
    sqlTests.put("\"Albert D'souza\"", "\"\"Albert D''souza\"\"");

    urlTests = new HashMap<String, String>();

    urlTests.put("*:*", URLEncoder.encode("*:*", ENCODING));
    urlTests.put("price:[* TO 200]", URLEncoder.encode("price:[* TO 200]",
            ENCODING));
    urlTests.put("review:\"hybrid sedan\"", URLEncoder.encode(
            "review:\"hybrid sedan\"", ENCODING));
  }

  /**
   * Test method for
   * {@link EvaluatorBag#getSqlEscapingEvaluator()}.
   */
  @Test
  public void testGetSqlEscapingEvaluator() {
    Evaluator sqlEscaper = EvaluatorBag.getSqlEscapingEvaluator();
    runTests(sqlTests, sqlEscaper);
  }

  /**
   * Test method for
   * {@link EvaluatorBag#getUrlEvaluator()}.
   */
  @Test
  public void testGetUrlEvaluator() throws Exception {
    Evaluator urlEvaluator = EvaluatorBag.getUrlEvaluator();
    runTests(urlTests, urlEvaluator);
  }

  /**
   * Test method for
   * {@link EvaluatorBag#getDateFormatEvaluator()}.
   */
  @Test
  @Ignore
  public void testGetDateFormatEvaluator() {
    Evaluator dateFormatEval = EvaluatorBag.getDateFormatEvaluator();
    assertEquals(new SimpleDateFormat("yyyy-MM-dd").format(new Date()),
            dateFormatEval.evaluate(resolver, "'NOW',yyyy-MM-dd HH:mm"));

    Map<String, Object> map = new HashMap<String, Object>();
    map.put("key", new Date());
    resolver.addNamespace("A", map);

    assertEquals(new SimpleDateFormat("yyyy-MM-dd HH:mm").format(new Date()),
            dateFormatEval.evaluate(resolver, "A.key, yyyy-MM-dd HH:mm"));
  }

  private void runTests(Map<String, String> tests, Evaluator evaluator) {
    for (Map.Entry<String, String> entry : tests.entrySet()) {
      Map<String, Object> values = new HashMap<String, Object>();
      values.put("key", entry.getKey());
      resolver.addNamespace("A", values);

      String expected = (String) entry.getValue();
      String actual = evaluator.evaluate(resolver, "A.key");
      assertEquals(expected, actual);
    }
  }
}
